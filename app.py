
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import requests

app = FastAPI()

openai.api_key = os.environ.get("OPENAI_API_KEY")
newsapi_key = os.environ.get("NEWSAPI_KEY")

if not openai.api_key:
    raise ValueError("Переменная окружения OPENAI_API_KEY не установлена")
if not newsapi_key:
    raise ValueError("Переменная окружения NEWSAPI_KEY не установлена")

class Topic(BaseModel):
    topic: str

def get_recent_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={newsapi_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Ошибка при получении данных из NewsAPI")
    articles = response.json().get("articles", [])
    if not articles:
        return "Свежих новостей не найдено."
    return "\n".join(article["title"] for article in articles[:3])

def generate_post(topic):
    recent_news = get_recent_news(topic)

    prompt_title = f"Придумайте привлекательный заголовок для поста на тему: {topic}"
    response_title = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_title}],
        max_tokens=50,
        temperature=0.7,
    )
    title = response_title.choices[0].message.content.strip()

    prompt_post = (
        f"Напишите подробный пост для блога на тему: {topic}, учитывая следующие последние новости:\n"
        f"{recent_news}\n\n"
        "Используйте короткие абзацы и ключевые слова для лучшего восприятия и SEO."
    )
    response_post = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_post}],
        max_tokens=1000,
        temperature=0.7,
    )
    post_content = response_post.choices[0].message.content.strip()

    return {"title": title, "post_content": post_content}

@app.post("/generate-post")
async def generate_post_api(topic: Topic):
    return generate_post(topic.topic)

@app.get("/heartbeat")
async def heartbeat_api():
    return {"status": "OK"}
