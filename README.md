<div align="center">

# $\textcolor{#17365D}{YouTube\ Comment\ Topic\ Modeling}$

### Multilingual E5 · UMAP · HDBSCAN · BERTopic

<picture><img src="https://img.shields.io/badge/Python-3.11-17365D?style=for-the-badge&amp;logo=python&amp;logoColor=white" alt="Python 3.11"></picture>
<picture><img src="https://img.shields.io/badge/Embeddings-Multilingual_E5-6F42C1?style=for-the-badge" alt="Multilingual E5"></picture>
<picture><img src="https://img.shields.io/badge/Reduction-UMAP-087E8B?style=for-the-badge" alt="UMAP"></picture>
<picture><img src="https://img.shields.io/badge/Clustering-HDBSCAN-1E7145?style=for-the-badge" alt="HDBSCAN"></picture>
<picture><img src="https://img.shields.io/badge/Topics-BERTopic-8B1E2D?style=for-the-badge" alt="BERTopic"></picture>
<picture><img src="https://img.shields.io/badge/Output-Excel_XLSX-B7791F?style=for-the-badge" alt="Excel files"></picture>

**CLEAN · EMBED · REDUCE · CLUSTER · LABEL · EXPORT**

*Analyze already-collected comments and discover multilingual discussion topics.*

</div>

---

## $\textcolor{#17365D}{01.\ Project\ Overview}$

This Python project discovers and organizes themes in **previously collected YouTube comments or other short texts**. It reads an Excel spreadsheet, cleans and filters the text, creates semantic embeddings, identifies groups of similar comments, and exports the topic assignments and summaries as Excel files.

**This script does not download comments from YouTube.** Its input is an existing Excel dataset.

| Item | Value |
|:--|:--|
| Input file | `comments.xlsx` |
| Required Excel column | `text` (exact spelling) |
| Main Python script | `main me5bert.py` |
| Dependencies | `requirements.txt` in this folder |
| Generated output directory | `data/` |
| Main purpose | Exploratory, multilingual topic discovery and research |

## $\textcolor{#17365D}{02.\ What\ the\ Code\ Does}$

| Step | Operation | Details from the actual script |
|:--|:--|:--|
| **1 — Load** | Read input | `pandas.read_excel()` loads `comments.xlsx`; the original dataset shape is printed. |
| **2 — Clean** | Normalize text | Remove missing and blank texts, trim spaces, remove URLs and normalize repeated whitespace. |
| **3 — Filter** | Improve the dataset | Remove duplicate cleaned comments, texts shorter than **3 words**, and emoji-only/symbol-only entries without letters. |
| **4 — Embed** | Encode meaning | The `intfloat/multilingual-e5-base` SentenceTransformer turns each retained comment into a semantic vector, processing **8 texts per batch**. |
| **5 — Reduce** | UMAP | Reduce the embedding vectors to **5 dimensions**, using cosine distance to model semantic neighborhoods. |
| **6 — Cluster** | HDBSCAN | Group similar comments into density-based clusters; unassigned comments may receive topic **`-1`**. |
| **7 — Model topics** | BERTopic | Identify topic representations and request a reduction to approximately **10 topics**. |
| **8 — Label** | Automatic keywords | Name each detected topic by joining up to **4 highest-ranked topic words** with underscores. Topic `-1` is named `Uncategorized`. |
| **9 — Export** | Excel reports | Save topic summaries, comment-by-comment assignments, separate files for each topic, and representative documents. |

**Processing flow**

```text
comments.xlsx  →  Clean and deduplicate  →  E5 semantic embeddings
             →  UMAP (5 dimensions)      →  HDBSCAN clusters
             →  BERTopic                 →  Automatic topic labels
             →  Excel reports in data/
```

> [!NOTE]
> The exported assignments represent **cleaned, retained text records**, not all rows of the original spreadsheet. Records removed by preprocessing are not exported.

## $\textcolor{#17365D}{03.\ Models\ and\ Settings}$

These settings are taken directly from `main me5bert.py`, not from BERTopic examples or assumed defaults.

| Component | Actual settings | Purpose |
|:--|:--|:--|
| **Multilingual E5** | `intfloat/multilingual-e5-base`, `batch_size=8` | Generate multilingual semantic embeddings. |
| **UMAP** | `n_neighbors=15`, `n_components=5`, `min_dist=0.0`, `metric="cosine"`, `random_state=42` | Reduce embedding dimensions before clustering. |
| **HDBSCAN** | `min_cluster_size=50`, `metric="euclidean"`, `cluster_selection_method="eom"`, `prediction_data=True` | Identify dense groups of related comments and potential outliers. |
| **BERTopic** | `nr_topics=10`, `verbose=True` | Build topic representations and reduce topic count toward the requested target. |

The script generates embeddings itself with `model.encode(texts, ...)` and passes those vectors to `topic_model.fit_transform(texts, embeddings)`.

> [!IMPORTANT]
> `nr_topics=10` is a **reduction target**, not a guarantee of exactly ten meaningful topics. With `min_cluster_size=50`, small datasets or uncommon viewpoints may produce many outliers. The E5 input is encoded **without query/passage task prefixes** in this implementation.

## $\textcolor{#1C6849}{04.\ Installation\ and\ Run}$

**Requirements:** Python 3.11 is a suitable choice (the included Dockerfile uses `python:3.11-slim`), an internet connection for the initial model download, and the dependencies listed in this folder's `requirements.txt`.

1. Open a terminal **inside** the `me5_umap_hdbscan_bertopic.10` folder.
2. Place your input spreadsheet in that same folder, named exactly `comments.xlsx`.
3. Make sure the spreadsheet contains a column named exactly `text`.
4. Install dependencies, then run the actual script filename:

```bash
python -m pip install -r requirements.txt
python "main me5bert.py"
```

**Example Excel input**

| text |
|:--|
| I found this explanation useful and easy to understand. |
| We need more discussion about the environmental impacts. |
| The speaker provides an interesting perspective on the topic. |

The program prints progress information while loading the data, generating embeddings, fitting BERTopic, and saving the results. It creates the `data/` directory automatically. **No YouTube API key is required** for this analysis script.

> [!TIP]
> `INPUT_FILE` and `OUTPUT_FOLDER` are relative paths in the source code. Run the command from the directory containing `comments.xlsx`, or adjust these variables in the script.

## $\textcolor{#17365D}{05.\ Generated\ Excel\ Files}$

| File | Contents |
|:--|:--|
| `data/topic_summary.xlsx` | Overview returned by `get_topic_info()`: topic IDs, topic sizes and available topic representation fields. |
| `data/all_topics_full.xlsx` | Each retained comment's `text`, numerical `topic`, automatically generated `topic_label`, and `confidence` value returned by BERTopic. |
| `data/topic_files/topic_*.xlsx` | A separate spreadsheet for **every observed topic ID**, including `-1` if unassigned comments occur. |
| `data/representative_docs.xlsx` | Up to **5 representative comments per non-outlier topic**, with `topic_id`, `topic_label`, and `document`. |

**Typical output layout**

```text
data/
├── topic_summary.xlsx
├── all_topics_full.xlsx
├── representative_docs.xlsx
└── topic_files/
    ├── topic_0_<keywords>.xlsx
    ├── topic_1_<keywords>.xlsx
    └── topic_-1_Uncategorized.xlsx  (when applicable)
```

The names of the individual topic files depend on the topic keywords found in the dataset.

## $\textcolor{#17365D}{06.\ How\ to\ Interpret\ Results}$

- **`topic`**: cluster/topic identifier. `-1` identifies comments not assigned to a topic cluster.
- **`topic_label`**: automatically generated keywords, **not** an expert-validated or natural-language topic title.
- **`confidence`**: the value returned by BERTopic for that assignment; it is **not a calibrated measure of scientific certainty** or overall topic quality.
- **`topic_summary.xlsx`**: useful for comparing topic prevalence and inspecting the main representative words.
- **Representative documents**: examples to read before interpreting and naming clusters in a research report.

For academic work, inspect the actual comments, check the interpretability of the clusters, and verify important conclusions manually.

## $\textcolor{#8B1E2D}{07.\ Important\ Limitations}$

> [!WARNING]
> This module **does not** download YouTube comments, perform sentiment analysis, produce topic visualization charts, save a trained model, or resume an interrupted model run.

- The final `all_topics_full.xlsx` file does **not** preserve other source spreadsheet fields such as user name, likes, video ID, or publication date.
- Identical cleaned comments are deduplicated even when they may have come from different people.
- Comments with fewer than three words, no letters, or only symbols are excluded.
- Outliers and the final number of topics depend on the input dataset and clustering settings.
- Automatically generated labels should be reviewed before publication or decision-making.
- Filenames derived from topic words could require extra sanitization for unusual characters or very long names.
- This script contains no explicit exception handling for an empty cleaned dataset, a missing `text` column, or an unavailable model download.

---

<div align="center">

## $\textcolor{#8B1E2D}{Persian\ Guide}$

<picture><img src="https://img.shields.io/badge/LANGUAGE-PERSIAN-7B2CBF?style=for-the-badge" alt="Persian language"></picture>
<picture><img src="https://img.shields.io/badge/DOCUMENTATION-FA_%2B_EN-17365D?style=for-the-badge" alt="English and Persian documentation"></picture>

</div>

<div dir="rtl" align="right">

<h2>🔷 ۱. معرفی برنامه</h2>

<p>این برنامه برای <strong>کشف موضوعات و دسته‌بندی معنایی نظرات یوتیوب</strong> و سایر متن‌های کوتاه طراحی شده است. ابتدا متن‌های موجود در فایل اکسل را پاک‌سازی می‌کند، سپس با کمک مدل زبانی چندزبانه برای هر نظر یک بردار معنایی می‌سازد و در نهایت نظرات مشابه را در گروه‌های موضوعی قرار می‌دهد.</p>

<p><strong>توجه:</strong> این برنامه نظرات را از یوتیوب دانلود نمی‌کند؛ فقط اطلاعاتی را تحلیل می‌کند که قبلاً جمع‌آوری شده و در فایل اکسل قرار گرفته‌اند.</p>

<h2>🔷 ۲. مراحل پردازش داده‌ها</h2>

<ol>
<li><strong>خواندن فایل:</strong> برنامه فایل <code>comments.xlsx</code> را می‌خواند. باید ستونی با نام دقیق <code>text</code> وجود داشته باشد.</li>
<li><strong>پاک‌سازی:</strong> نظرهای خالی، آدرس‌های اینترنتی و فاصله‌های اضافی حذف می‌شوند. سپس نظرهای تکراری کنار گذاشته می‌شوند.</li>
<li><strong>حذف داده‌های کم‌اطلاعات:</strong> متن‌های کمتر از سه واژه و نظرهای بدون حروف، مانند پیام‌های صرفاً شامل شکلک، از تحلیل حذف می‌شوند.</li>
<li><strong>تبدیل متن به بردار معنایی:</strong> مدل <code>intfloat/multilingual-e5-base</code> محتوای هر نظر را به یک بردار عددی تبدیل می‌کند. پردازش در دسته‌های هشت‌تایی انجام می‌شود.</li>
<li><strong>کاهش ابعاد:</strong> الگوریتم <code>UMAP</code> بردارها را به پنج بُعد کاهش می‌دهد تا خوشه‌بندی امکان‌پذیرتر شود.</li>
<li><strong>خوشه‌بندی:</strong> الگوریتم <code>HDBSCAN</code> نظرات نزدیک از نظر معنا را گروه‌بندی می‌کند. به نظرات بدون خوشه معتبر ممکن است شناسه <code>-1</code> اختصاص داده شود.</li>
<li><strong>کشف و تنظیم موضوعات:</strong> مدل <code>BERTopic</code> موضوع‌ها و واژه‌های شاخص را استخراج می‌کند و برای کاهش تعداد موضوع‌ها به حدود ده موضوع تلاش می‌کند.</li>
<li><strong>نام‌گذاری:</strong> نام خودکار هر موضوع از حداکثر چهار واژه شاخص آن ساخته می‌شود.</li>
<li><strong>ذخیره:</strong> خلاصه موضوع‌ها، نتایج تمام نظرات باقی‌مانده، فایل مستقل هر موضوع و نمونه‌نظرهای نماینده ذخیره می‌شوند.</li>
</ol>

<h2>🔷 ۳. تنظیمات اصلی مدل‌ها</h2>

<ul>
<li><strong>مدل معنایی:</strong> <code>multilingual-e5-base</code></li>
<li><strong>اندازه هر دسته پردازش:</strong> <code>8</code></li>
<li><strong>تنظیمات کاهش ابعاد:</strong> <code>n_neighbors=15</code> و <code>n_components=5</code></li>
<li><strong>حداقل اندازه خوشه:</strong> <code>min_cluster_size=50</code></li>
<li><strong>هدف تعداد موضوع‌ها:</strong> <code>nr_topics=10</code></li>
</ul>

<p>این تنظیمات ممکن است برای همه مجموعه‌داده‌ها مناسب نباشند؛ به‌ویژه اگر تعداد نظرات کم باشد، احتمال افزایش نظرهای بدون خوشه وجود دارد. عدد ده نیز تضمین نمی‌کند که دقیقاً ده موضوع معنادار ایجاد شوند.</p>

<h2>🟢 ۴. نصب و اجرای برنامه</h2>

<p>در پوشه <code>me5_umap_hdbscan_bertopic.10</code> فایلی با نام <code>comments.xlsx</code> قرار بده و مطمئن شو که ستون <code>text</code> دارد. سپس در همان پوشه، فرمان‌های زیر را اجرا کن:</p>

</div>

```bash
python -m pip install -r requirements.txt
python "main me5bert.py"
```

<div dir="rtl" align="right">

<p>برنامه به‌طور خودکار پوشه <code>data</code> را برای نتایج ایجاد می‌کند. اجرای نخست ممکن است به دانلود مدل زبانی نیاز داشته باشد. برای این مرحله کلید API یوتیوب لازم نیست.</p>

<h2>🔷 ۵. فایل‌های خروجی</h2>

<ul>
<li><strong>خلاصه موضوع‌ها:</strong> <code>data/topic_summary.xlsx</code> شامل شناسه موضوع‌ها، تعداد نظرات و اطلاعات مربوط به واژه‌های شاخص است.</li>
<li><strong>نتیجه کامل نظرات:</strong> <code>data/all_topics_full.xlsx</code> شامل متن نظر، شماره موضوع، نام موضوع و مقدار <code>confidence</code> است.</li>
<li><strong>فایل جداگانه برای هر موضوع:</strong> پوشه <code>data/topic_files/</code> برای موضوعات شناسایی‌شده فایل‌های مستقل ایجاد می‌کند.</li>
<li><strong>نظرهای نمونه:</strong> <code>data/representative_docs.xlsx</code> تا پنج نظر نماینده برای هر موضوع غیرپرت ذخیره می‌کند.</li>
</ul>

<h2>🔴 ۶. نکات مهم و محدودیت‌ها</h2>

<ul>
<li>ستون‌های دیگر فایل اولیه، مانند نام نویسنده، تاریخ یا تعداد لایک، به فایل نهایی همه موضوع‌ها منتقل نمی‌شوند.</li>
<li>نظرهای تکراری، بسیار کوتاه یا بدون حروف از تحلیل حذف می‌شوند.</li>
<li>شناسه <code>-1</code> معمولاً به نظرهایی مربوط است که در هیچ خوشه معتبری قرار نگرفته‌اند.</li>
<li>نام موضوع‌ها به‌صورت خودکار از واژه‌های شاخص ساخته می‌شود و باید توسط پژوهشگر بررسی شود.</li>
<li>مقدار <code>confidence</code> به‌تنهایی معیار قطعی کیفیت دسته‌بندی یا اعتبار علمی نتایج نیست.</li>
<li>این نسخه تحلیل احساسات، رسم نمودار، ذخیره مدل آموزش‌دیده و ادامه خودکار پردازش قطع‌شده را انجام نمی‌دهد.</li>
</ul>

<p><strong>کاربرد پژوهشی:</strong> این ابزار برای شناسایی محورهای بحث، مطالعه گفت‌وگوهای عمومی، پژوهش‌های رسانه‌ای و تحلیل مجموعه‌های بزرگ نظرات قابل استفاده است؛ اما تفسیر نهایی موضوع‌ها باید با بررسی انسانی انجام شود.</p>

</div>

---

<div align="center">

**Multilingual Topic Discovery · Explainable Exports · Research-Oriented Analysis**

</div>
