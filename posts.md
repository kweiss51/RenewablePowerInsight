---
layout: page
title: All Posts
permalink: /posts/
---

<div class="posts-page">
  <h1>All Energy Blog Posts</h1>
  
  {% if site.posts.size > 0 %}
    <p>{{ site.posts.size }} posts total</p>
    
    <div class="post-list">
      {% for post in site.posts %}
        <article class="post-item">
          <header class="post-header">
            <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</span>
            <h2 class="post-title">
              <a class="post-link" href="{{ post.url | relative_url }}">
                {{ post.title | escape }}
              </a>
            </h2>
          </header>
          
          <div class="post-content">
            {% if post.excerpt %}
              {{ post.excerpt | markdownify | truncatewords: 50 }}
            {% else %}
              {{ post.content | markdownify | strip_html | truncatewords: 50 }}
            {% endif %}
          </div>
          
          <div class="post-meta-info">
            {% if post.topic %}
              <span class="post-topic">📂 {{ post.topic }}</span>
            {% endif %}
            {% if post.word_count %}
              <span class="post-word-count">📝 {{ post.word_count }} words</span>
            {% endif %}
            {% if post.reading_time %}
              <span class="post-reading-time">⏱️ {{ post.reading_time }} min read</span>
            {% endif %}
          </div>
          
          {% if post.tags and post.tags.size > 0 %}
            <div class="post-tags">
              {% for tag in post.tags limit: 5 %}
                <span class="tag">{{ tag }}</span>
              {% endfor %}
            </div>
          {% endif %}
          
          <footer class="post-footer">
            <a href="{{ post.url | relative_url }}" class="read-more">Read Full Article →</a>
          </footer>
        </article>
      {% endfor %}
    </div>
  {% else %}
    <p>No posts found. Check back soon for new energy content!</p>
  {% endif %}
</div>

<style>
.posts-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.post-list {
  margin-top: 2em;
}

.post-item {
  margin-bottom: 3em;
  padding: 2em;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.post-header {
  margin-bottom: 1em;
}

.post-meta {
  font-size: 0.9em;
  color: #6a737d;
  display: block;
  margin-bottom: 0.5em;
}

.post-title {
  margin: 0;
  font-size: 1.5em;
  line-height: 1.3;
}

.post-link {
  color: #0366d6;
  text-decoration: none;
}

.post-link:hover {
  text-decoration: underline;
}

.post-content {
  margin: 1em 0;
  color: #24292e;
  line-height: 1.6;
}

.post-meta-info {
  margin: 1em 0;
  font-size: 0.85em;
}

.post-meta-info span {
  margin-right: 1em;
  color: #6a737d;
}

.post-tags {
  margin: 1em 0;
}

.tag {
  background: #f1f8ff;
  color: #0366d6;
  padding: 0.25em 0.5em;
  border-radius: 3px;
  font-size: 0.8em;
  margin-right: 0.5em;
  display: inline-block;
  margin-bottom: 0.25em;
}

.post-footer {
  margin-top: 1.5em;
  padding-top: 1em;
  border-top: 1px solid #e1e4e8;
}

.read-more {
  color: #0366d6;
  text-decoration: none;
  font-weight: 500;
}

.read-more:hover {
  text-decoration: underline;
}
</style>
