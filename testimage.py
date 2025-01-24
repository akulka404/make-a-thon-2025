from openai import OpenAI
client = OpenAI()
# 
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://media.gettyimages.com/id/1131356455/photo/old-banana.jpg?s=2048x2048&w=gi&k=20&c=EmR3WuumadrBA6lvw6CLq2c8h28t83mcxO1rRu7UoQg=",
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

print(response.choices[0])
