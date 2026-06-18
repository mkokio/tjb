"""Seed the database with the prototype's sample bilingual content.

Idempotent: re-running updates existing rows (keyed by slug). Ported verbatim
from the design prototype's data.jsx.

    python manage.py seed_demo
"""

from datetime import datetime

from django.core.management.base import BaseCommand

from blog.models import Author, Post

# Source labels (from the prototype) → current category slugs. Bikes & Parts
# now share the "Bike/Parts" category; the retired "Culture" folds into "Other".
CATEGORY_SLUG = {
    "Bikes": "bikes",
    "Parts": "bikes",
    "Places to Ride": "places",
    "Opinions": "opinions",
    "Interviews": "interviews",
    "Culture": "other",
    "Other": "other",
}

AUTHORS = {
    "Marc": {
        "slug": "marc", "handle": "@marc", "avatar": "マーク", "writes": "en",
        "location_en": "Shizuoka", "location_ja": "静岡",
        "role_en": "Founder · wrench · dad", "role_ja": "創設者・整備士・父",
        "since_en": "Riding here since 2014", "since_ja": "2014年からここで走ってる",
        "bio_en": "Builds bikes in a too-small shed, rides tea-road switchbacks before work, and is on a one-man mission to prove Shizuoka has the best dirt in Japan. Reviews things honestly, even his own bikes.",
        "bio_ja": "狭すぎる小屋でバイクを組み、仕事前に茶畑のヘアピンを上る。静岡には日本一の土があると証明する一人ミッション中。自分のバイクにも正直なレビューを書く。",
    },
    "Koyna": {
        "slug": "koyna", "handle": "@koyna", "avatar": "コヤ", "writes": "ja",
        "location_en": "Nagoya", "location_ja": "名古屋",
        "role_en": "Words & interviews", "role_ja": "文章とインタビュー",
        "since_en": "Writing here since 2015", "since_ja": "2015年からここで書いてる",
        "bio_en": "Collects words the way other people collect parts. Interviews the quiet people behind the loud bikes. Believes 'jitensha' and 'bike' are two different machines, and will tell you why.",
        "bio_ja": "他人がパーツを集めるように、言葉を集める。派手なバイクの裏にいる静かな人々にインタビューする。「自転車」と「バイク」は別の乗り物だと信じていて、その理由を語る。",
    },
}

POSTS = [
    {
        "slug": "shizuoka-trails", "cat": "Places to Ride", "orig": "en", "author": "Marc",
        "date": "June 6, 2026", "read": "9 min", "media": "shizuoka ridgeline",
        "title_en": "The trails in and around Shizuoka, reviewed",
        "sub_en": "Tea fields up top, the sea on the horizon, and more loam than anyone gives this prefecture credit for.",
        "title_ja": "静岡市周辺のトレイル、走ってみた",
        "sub_ja": "頂上には茶畑、地平線には海。そして、この県が評価されている以上のローム土がある。",
    },
    {
        "slug": "stp20-showoff", "cat": "Bikes", "orig": "en", "author": "Marc",
        "date": "June 4, 2026", "read": "5 min", "media": "STP 20 build",
        "title_en": "STP 20 show-off: a small bike with big opinions",
        "sub_en": "Why the little Specialized hardtail might be the most honest bike in the shed.",
        "title_ja": "STP 20 自慢:小さいバイク、大きな主張",
        "sub_ja": "この小さなハードテイルが、もしかしたら一番正直なバイクかもしれない理由。",
    },
    {
        "slug": "bike-vs-jitensha", "cat": "Opinions", "orig": "ja", "author": "Koyna",
        "date": "June 1, 2026", "read": "7 min", "media": "three bikes lined up",
        "title_ja": "バイク vs 自転車 vs マウンテンバイク",
        "sub_ja": "言葉ひとつで、乗り物への気持ちはこんなにも変わる。日本語の「自転車」という言葉について。",
        "title_en": "Bike vs. jitensha vs. mountain bike",
        "sub_en": "One word changes how you feel about the machine under you. On the Japanese word 'jitensha'.",
    },
    {
        "slug": "marc-bikes-history", "cat": "Bikes", "orig": "en", "author": "Marc",
        "date": "May 30, 2026", "read": "11 min", "media": "twelve frames, one shed",
        "title_en": "Marc's bikes: a history in twelve frames",
        "sub_en": "Every bike I've owned in Japan, why I bought it, and why most of them are already gone.",
        "title_ja": "マークのバイク史：12台の記録",
        "sub_ja": "日本で所有してきた全てのバイク。なぜ買い、そしてなぜその多くを手放したのか。",
    },
    {
        "slug": "kids-bikes", "cat": "Bikes", "orig": "en", "author": "Marc",
        "date": "May 28, 2026", "read": "8 min", "media": "strider + 16in + helmet",
        "title_en": "Kids' bikes: Strider, the 16-incher, the towel, the helmet",
        "sub_en": "A field guide to getting small humans rolling without the tears (mostly theirs).",
        "title_ja": "子供のバイク:ストライダー、16インチ、タオル、ヘルメット",
        "sub_ja": "小さな人間を涙なし(だいたい本人の)で走らせるためのフィールドガイド。",
    },
    {
        "slug": "monotaro", "cat": "Parts", "orig": "en", "author": "Marc",
        "date": "May 24, 2026", "read": "4 min", "media": "cardboard box of parts",
        "title_en": "In praise of MonotaRO",
        "sub_en": "An ode to the industrial-supply catalogue that quietly keeps every home workshop in Japan alive.",
        "title_ja": "モノタロウ礼賛",
        "sub_ja": "日本中の作業場をひっそりと支える、あの工業用品カタログへの賛歌。",
    },
    {
        "slug": "simworks", "cat": "Interviews", "orig": "en", "author": "Koyna",
        "date": "May 20, 2026", "read": "12 min", "media": "simworks studio",
        "title_en": "SimWorks and the cool, quiet vision",
        "sub_en": "How a Nagoya shop turned a love of niche parts into a worldwide language of taste.",
        "title_ja": "シムワークスの、静かでクールなビジョン",
        "sub_ja": "名古屋のショップが、ニッチなパーツへの愛をいかにして世界共通の「趣味」の言語に変えたか。",
    },
    {
        "slug": "confidence", "cat": "Opinions", "orig": "en", "author": "Koyna",
        "date": "May 16, 2026", "read": "6 min", "media": "marketing copy collage",
        "title_en": "'Confidence' is doing too much in bike marketing",
        "sub_en": "Every press release promises it. Nobody can tell you what it weighs.",
        "title_ja": "自転車マーケティングの「自信(コンフィデンス)」は働きすぎだ",
        "sub_ja": "どのプレスリリースもそれを約束する。でも、それが何グラムか誰も言えない。",
    },
    {
        "slug": "mint-sauce", "cat": "Culture", "orig": "en", "author": "Marc",
        "date": "May 12, 2026", "read": "3 min", "media": "a sheep on a hill",
        "title_en": "Mint Sauce, and riding for no reason at all",
        "sub_en": "The little cartoon sheep that taught a generation what mountain biking is actually about.",
        "title_ja": "ミントソースと、理由なんてない走り",
        "sub_ja": "マウンテンバイクの本当の意味を一世代に教えた、小さな漫画の羊。",
    },
    {
        "slug": "parts-bin", "cat": "Parts", "orig": "ja", "author": "Koyna",
        "date": "May 8, 2026", "read": "5 min", "media": "a glorious parts bin",
        "title_ja": "「パーツビン・バイク」と、その他の言葉",
        "sub_ja": "余り物で組んだ一台が、なぜか一番愛おしい。自転車にまつわる小さな言葉たち。",
        "title_en": "The parts-bin bike, and other good words",
        "sub_en": "The bike built from leftovers is somehow the most loved. A small glossary of cycling words.",
    },
    {
        "slug": "bicycle-flowchart", "cat": "Other", "orig": "en", "author": "Koyna",
        "date": "May 5, 2026", "read": "2 min", "media": "a decision flowchart",
        "title_en": "A flowchart for choosing your next bicycle",
        "sub_en": "Answer six slightly judgmental questions and arrive, inevitably, at 'just ride what you already have'.",
        "title_ja": "次の一台を選ぶためのフローチャート",
        "sub_ja": "ちょっと意地悪な6つの質問に答えれば、必然的に「今あるやつに乗れ」に辿り着く。",
    },
]

BODIES = {
    "shizuoka-trails": {
        "en": [
            {"t": "p", "x": "Everyone drives past Shizuoka. Bullet train at 285 km/h, eyes on a phone, Fuji on the left if the clouds allow it. What almost nobody does is stop, point a car up one of the tea-road switchbacks, and go looking for dirt. They should."},
            {"t": "p", "x": "The prefecture is a long, thin smile of coastline backed immediately by mountains. That geography does something rare: you can climb through a tea plantation in the morning fog and, ninety minutes later, be looking at the Pacific from the top of a descent that has no business being this good."},
            {"t": "img", "label": "tea-field switchback", "cap": "The climb is the price of admission. Pay it slowly."},
            {"t": "quote", "x": "There is more loam here than anyone gives this prefecture credit for — you just have to be willing to get lost finding it."},
            {"t": "p", "x": "Below are the three loops worth the train ticket, ranked not by difficulty but by how much they'll make you reconsider where you live."},
            {"t": "ol", "items": [
                "Nihondaira to the coast — mellow, fast, and absurdly scenic. Start here.",
                "The Abe River back-valleys — steeper, looser, fewer people, more frogs.",
                "Umegashima, up near the hot springs — alpine feel, a long day, a better onsen.",
            ]},
            {"t": "p", "x": "Bring more water than you think. Bring a towel. Bring 200 yen for the vending machine at the trailhead that, against all logic, sells hot corn soup in summer."},
        ],
        "ja": [
            {"t": "p", "x": "みんな静岡を通り過ぎる。時速285キロの新幹線、スマホに落とした視線、雲が許せば左手に富士山。ほとんど誰もやらないのは、車を停めて、茶畑のヘアピンを上り、土を探しに行くことだ。やるべきなのに。"},
            {"t": "p", "x": "この県は、細長い海岸線の笑顔のすぐ背後に山が迫っている。その地形が、めったにないことを起こす。朝霧の茶畑を上り、90分後には、こんなに良くていいのかという下りの頂上から太平洋を眺めている。"},
            {"t": "img", "label": "茶畑のヘアピン", "cap": "上りは入場料。ゆっくり払おう。"},
            {"t": "quote", "x": "この県が評価されている以上に、ここにはローム土がある。ただ、それを探して迷子になる覚悟がいるだけだ。"},
            {"t": "p", "x": "以下は、新幹線代に値する3つのループ。難易度ではなく、「自分の住んでいる場所を考え直させる度」で並べた。"},
            {"t": "ol", "items": [
                "日本平から海へ — 緩やかで速く、馬鹿げて景色がいい。まずはここから。",
                "安倍川の奥の谷 — 急で、ルーズで、人が少なく、蛙が多い。",
                "梅ヶ島、温泉の近く — アルパインな雰囲気、長い一日、そしてより良い温泉。",
            ]},
            {"t": "p", "x": "思っているより多めに水を持って。タオルも。そして登山口の自動販売機用に200円を。論理に反して、夏でもホットなコーンスープを売っているから。"},
        ],
    },
    "monotaro": {
        "en": [
            {"t": "p", "x": "There is a particular kind of happiness that arrives in a brown cardboard box with a cat on the tape. If you have ever kept a bicycle alive in Japan, you know the cat. The cat is MonotaRO."},
            {"t": "p", "x": "It is, on paper, an industrial-supply catalogue — the place factories buy bolts and gloves and degreaser by the drum. But somewhere along the way it became the quiet backbone of every home workshop in the country. Need an M5×16 in titanium at 11pm? It's there. Need it tomorrow? Also there."},
            {"t": "quote", "x": "A bike shop sells you a bicycle. MonotaRO sells you the right to fix it yourself, forever."},
            {"t": "img", "label": "the famous brown box", "cap": "You learn to recognise the cat before you can read the kanji."},
            {"t": "p", "x": "I am not being paid to write this. That is, somehow, the point. There is no romance in a part number. And yet here I am, romanticising one."},
        ],
        "ja": [
            {"t": "p", "x": "ガムテープに猫が描かれた茶色いダンボール箱で届く、特別な幸せがある。日本で自転車を生かし続けたことがあるなら、あの猫を知っているはずだ。あの猫は、モノタロウだ。"},
            {"t": "p", "x": "建前上は工業用品のカタログだ。工場がボルトや手袋や脱脂剤をドラム単位で買う場所。でもいつの間にか、この国のすべての作業場の静かな屋台骨になっていた。夜11時にチタンのM5×16が要る?ある。明日要る?それもある。"},
            {"t": "quote", "x": "自転車屋はあなたに自転車を売る。モノタロウは、それを自分で直し続ける権利を売る。"},
            {"t": "img", "label": "あの有名な茶色い箱", "cap": "漢字が読めるようになる前に、猫を見分けられるようになる。"},
            {"t": "p", "x": "これを書いてお金をもらっているわけではない。むしろ、それこそが要点だ。品番にロマンはない。なのに僕は今、ひとつの品番にロマンを感じている。"},
        ],
    },
}


class Command(BaseCommand):
    help = "Seed the database with the prototype's sample bilingual content."

    def handle(self, *args, **options):
        authors = {}
        for name, data in AUTHORS.items():
            author, _ = Author.objects.update_or_create(name=name, defaults=data)
            authors[name] = author
        self.stdout.write(self.style.SUCCESS(f"Authors: {len(authors)}"))

        for p in POSTS:
            date = datetime.strptime(p["date"], "%B %d, %Y").date()
            bodies = BODIES.get(p["slug"], {})
            Post.objects.update_or_create(
                slug=p["slug"],
                defaults={
                    "category": CATEGORY_SLUG[p["cat"]],
                    "author": authors[p["author"]],
                    "date": date,
                    "read_time": p["read"],
                    "orig": p["orig"],
                    "title_en": p.get("title_en", ""),
                    "title_ja": p.get("title_ja", ""),
                    "sub_en": p.get("sub_en", ""),
                    "sub_ja": p.get("sub_ja", ""),
                    "body_en": bodies.get("en", []),
                    "body_ja": bodies.get("ja", []),
                    "media_label": p["media"],
                    "media_shape": "wide",
                    "published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Posts: {len(POSTS)}"))
