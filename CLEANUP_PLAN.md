# File Structure Cleanup Plan

## Files to Remove (Obsolete/Duplicate)

### Duplicate Index Files
- index_backup.html ❌
- index_clean.html ❌
- index_html_backup.html ❌
- index_old.html ❌
- index_simple.html ❌ (keep index.html only)
- test.html ❌

### Obsolete Python Files
- app.py ❌ (replaced by simple_blog_app.py)
- demo_ml_system.py ❌ (functionality moved to ml_models/)
- setup_ml.py ❌ (functionality in ml_models/)
- test_ml_system.py ❌ (functionality in ml_models/)
- fix_duplicate_tables.py ❌ (one-time script)
- fix_image_formatting.py ❌ (one-time script)
- add_images_to_posts.py ❌ (functionality in ml_models/blog_image_integrator.py)

### Obsolete Shell Scripts
- start.sh ❌ (functionality in automation_controller.py)
- deploy.sh ❌ (functionality in github_pages_generator.py)

### Documentation Files to Remove
- PROGRESS_BAR_GUIDE.md ❌
- SYSTEM_STATUS.md ❌ (outdated)
- LAUNCH_REPORT.md ❌

### Backup Files
- Gemfile.backup ❌
- posts.md ❌ (posts.html has been removed)
- requirements_minimal.txt ❌ (keep requirements.txt)

## Files to Reorganize

### Move to scripts/ directory
- automation_controller.py → scripts/
- control_panel.py → scripts/
- daily_automation.py → scripts/
- integrated_blog_system.py → scripts/
- github_pages_generator.py → scripts/
- launch_github_pages.py → scripts/
- setup_automation.sh → scripts/

### Keep in root
- simple_blog_app.py (main application)
- index.html (working homepage)
- posts.html (removed)
- about.md
- README.md
- requirements.txt
- _config.yml
- Gemfile

## Directory Structure After Cleanup

```
RenewablePowerInsight/
├── README.md
├── requirements.txt
├── _config.yml
├── Gemfile
├── index.html
<!-- posts.html removed -->
├── about.md
├── 404.html
├── simple_blog_app.py (main app)
├── scripts/
│   ├── automation_controller.py
│   ├── control_panel.py
│   ├── daily_automation.py
│   ├── integrated_blog_system.py
│   ├── github_pages_generator.py
│   ├── launch_github_pages.py
│   └── setup_automation.sh
├── src/
│   ├── news_scraper.py
│   └── blog_generator.py
├── ml_models/
│   └── (all ML components)
├── assets/
├── data/
├── logs/
├── templates/
├── _posts/
├── _includes/
└── _layouts/
```
