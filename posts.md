---
layout: default
title: All Articles
permalink: /posts/
---

<div class="posts-page">
  <header class="page-header">
    <h1>All Articles</h1>
    <p>Comprehensive coverage of renewable energy news and insights</p>
  </header>

  <div class="posts-list">
    {% for post in site.posts %}
      <article class="post-preview">
        <div class="post-meta">
          <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %d, %Y" }}</time>
          {% if post.category %}
            <span class="category">{{ post.category | capitalize }}</span>
          {% endif %}
        </div>
        
        <h2 class="post-title">
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </h2>
        
        {% if post.excerpt %}
          <div class="post-excerpt">
            {{ post.excerpt | strip_html | truncatewords: 30 }}
          </div>
        {% endif %}
        
        {% if post.tags %}
          <div class="post-tags">
            {% for tag in post.tags %}
              <span class="tag">{{ tag }}</span>
            {% endfor %}
          </div>
        {% endif %}
      </article>
    {% endfor %}
  </div>
</div>

<style>
.posts-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #666;
  font-size: 1.1rem;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.post-preview {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 2rem;
}

.post-preview:last-child {
  border-bottom: none;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.category {
  background: #e0f2fe;
  color: #0277bd;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 500;
}

.post-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.post-title a {
  color: #333;
  text-decoration: none;
  transition: color 0.3s;
}

.post-title a:hover {
  color: #2563eb;
}

.post-excerpt {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .posts-page {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .post-title {
    font-size: 1.3rem;
  }
  
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
