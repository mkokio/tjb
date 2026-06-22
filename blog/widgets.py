"""
blog/widgets.py

A Django admin widget that replaces the raw JSONField for body_en / body_ja
with a friendly block editor. Each block has a type (p, quote, img, ol, code)
and the widget builds the JSON invisibly.

Usage in admin.py:
    from .widgets import BlockEditorWidget
    from django import forms

    class PostAdminForm(forms.ModelForm):
        class Meta:
            model = Post
            fields = '__all__'
            widgets = {
                'body_en': BlockEditorWidget(),
                'body_ja': BlockEditorWidget(),
            }

    # then in PostAdmin:
    form = PostAdminForm
"""

import json
from django import forms
from django.utils.safestring import mark_safe


class BlockEditorWidget(forms.Widget):
    template_name = None  # we render directly in render()

    def render(self, name, value, attrs=None, renderer=None):
        # Parse existing value
        if isinstance(value, str):
            try:
                blocks = json.loads(value) if value else []
            except (json.JSONDecodeError, TypeError):
                blocks = []
        elif isinstance(value, list):
            blocks = value
        else:
            blocks = []

        widget_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'

        html = f'''
<div class="block-editor" id="editor_{widget_id}">
  <div class="block-list" id="blocks_{widget_id}"></div>
  <div class="block-add-row" style="margin-top:8px;">
    <select id="block_type_{widget_id}" style="margin-right:6px;">
      <option value="p">Paragraph</option>
      <option value="quote">Pull quote</option>
      <option value="img">Image</option>
      <option value="ol">Ordered list</option>
      <option value="code">Code</option>
    </select>
    <button type="button" onclick="addBlock_{widget_id}()"
            style="padding:4px 12px;">+ Add block</button>
  </div>
</div>
<textarea name="{name}" id="{widget_id}"
          style="display:none;">{self._encode(blocks)}</textarea>

<style>
.block-card {{
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 8px;
  background: #fafafa;
  position: relative;
}}
.block-card .block-type-label {{
  font-weight: bold;
  font-size: 11px;
  text-transform: uppercase;
  color: #666;
  margin-bottom: 6px;
}}
.block-card textarea, .block-card input[type=text] {{
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 13px;
  padding: 4px;
}}
.block-card textarea {{ min-height: 80px; resize: vertical; }}
.block-controls {{
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
}}
.block-controls button {{
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
}}
.ol-items {{ margin-bottom: 4px; }}
.ol-item {{ display: flex; gap: 4px; margin-bottom: 4px; }}
.ol-item input {{ flex: 1; }}
</style>

<script>
(function() {{
  var BLOCKS_{widget_id} = {self._encode(blocks)};

  function save() {{
    document.getElementById('{widget_id}').value = JSON.stringify(BLOCKS_{widget_id});
  }}

  function render() {{
    var container = document.getElementById('blocks_{widget_id}');
    container.innerHTML = '';
    BLOCKS_{widget_id}.forEach(function(block, i) {{
      container.appendChild(makeCard(block, i));
    }});
  }}

  function makeCard(block, i) {{
    var div = document.createElement('div');
    div.className = 'block-card';
    div.setAttribute('draggable', 'true');
    div.dataset.index = i;

    var label = document.createElement('div');
    label.className = 'block-type-label';
    label.textContent = blockLabel(block.t);
    div.appendChild(label);

    var controls = document.createElement('div');
    controls.className = 'block-controls';

    var upBtn = document.createElement('button');
    upBtn.type = 'button';
    upBtn.textContent = '↑';
    upBtn.title = 'Move up';
    upBtn.onclick = function() {{ if (i > 0) {{ move(i, i-1); }} }};

    var downBtn = document.createElement('button');
    downBtn.type = 'button';
    downBtn.textContent = '↓';
    downBtn.title = 'Move down';
    downBtn.onclick = function() {{ if (i < BLOCKS_{widget_id}.length - 1) {{ move(i, i+1); }} }};

    var delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.textContent = '✕';
    delBtn.title = 'Delete block';
    delBtn.style.color = '#c00';
    delBtn.onclick = function() {{ BLOCKS_{widget_id}.splice(i, 1); save(); render(); }};

    controls.appendChild(upBtn);
    controls.appendChild(downBtn);
    controls.appendChild(delBtn);
    div.appendChild(controls);

    // block-specific inputs
    if (block.t === 'p' || block.t === 'quote' || block.t === 'code') {{
      var ta = document.createElement('textarea');
      ta.value = block.x || '';
      ta.placeholder = block.t === 'quote' ? 'Pull quote text...' :
                       block.t === 'code'  ? 'Code...' : 'Paragraph text...';
      ta.oninput = function() {{ BLOCKS_{widget_id}[i].x = ta.value; save(); }};
      div.appendChild(ta);

    }} else if (block.t === 'img') {{
      var capInput = document.createElement('input');
      capInput.type = 'text';
      capInput.placeholder = 'Caption (optional)';
      capInput.value = block.cap || '';
      capInput.oninput = function() {{ BLOCKS_{widget_id}[i].cap = capInput.value; save(); }};

      var labelInput = document.createElement('input');
      labelInput.type = 'text';
      labelInput.placeholder = 'Image filename or URL';
      labelInput.value = block.label || '';
      labelInput.style.marginBottom = '4px';
      labelInput.oninput = function() {{ BLOCKS_{widget_id}[i].label = labelInput.value; save(); }};

      div.appendChild(labelInput);
      div.appendChild(capInput);

    }} else if (block.t === 'ol') {{
      var itemsDiv = document.createElement('div');
      itemsDiv.className = 'ol-items';

      function renderItems() {{
        itemsDiv.innerHTML = '';
        (BLOCKS_{widget_id}[i].items || []).forEach(function(item, j) {{
          var row = document.createElement('div');
          row.className = 'ol-item';
          var inp = document.createElement('input');
          inp.type = 'text';
          inp.value = item;
          inp.oninput = function() {{ BLOCKS_{widget_id}[i].items[j] = inp.value; save(); }};
          var rem = document.createElement('button');
          rem.type = 'button';
          rem.textContent = '✕';
          rem.onclick = function() {{ BLOCKS_{widget_id}[i].items.splice(j, 1); save(); renderItems(); }};
          row.appendChild(inp);
          row.appendChild(rem);
          itemsDiv.appendChild(row);
        }});
      }}
      renderItems();

      var addItem = document.createElement('button');
      addItem.type = 'button';
      addItem.textContent = '+ Add item';
      addItem.onclick = function() {{
        BLOCKS_{widget_id}[i].items = BLOCKS_{widget_id}[i].items || [];
        BLOCKS_{widget_id}[i].items.push('');
        save();
        renderItems();
      }};

      div.appendChild(itemsDiv);
      div.appendChild(addItem);
    }}

    return div;
  }}

  function blockLabel(t) {{
    return {{p:'Paragraph', quote:'Pull quote', img:'Image', ol:'List', code:'Code'}}[t] || t;
  }}

  function move(from, to) {{
    var tmp = BLOCKS_{widget_id}[from];
    BLOCKS_{widget_id}[from] = BLOCKS_{widget_id}[to];
    BLOCKS_{widget_id}[to] = tmp;
    save();
    render();
  }}

  window['addBlock_{widget_id}'] = function() {{
    var t = document.getElementById('block_type_{widget_id}').value;
    var block = {{t: t}};
    if (t === 'p' || t === 'quote' || t === 'code') block.x = '';
    else if (t === 'img') {{ block.label = ''; block.cap = ''; }}
    else if (t === 'ol') block.items = [''];
    BLOCKS_{widget_id}.push(block);
    save();
    render();
  }};

  // init
  render();
}})();
</script>
'''
        return mark_safe(html)

    def _encode(self, blocks):
        return json.dumps(blocks, ensure_ascii=False)

    def value_from_datadict(self, data, files, name):
        return data.get(name, '[]')