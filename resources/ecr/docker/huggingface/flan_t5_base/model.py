import os

import torch
from transformers import AutoTokenizer, pipeline


class TextGenerationLLM:
    def __init__(self, model_url: str = "google/flan-t5-base"):
        # make sure we don't connect to HF Hub
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        # setup text generation pipeline
        tokenizer = AutoTokenizer.from_pretrained(model_url, local_files_only=True)
        self.generator = pipeline(
            "text-generation",
            model=model_url,
            tokenizer=tokenizer,
            torch_dtype=torch.float16,
            device_map="auto",
            model_kwargs={"local_files_only": True},
        )
        self.generator.model = torch.compile(self.generator.model)

    def generate(self, prompt: str) -> str:
        results = self.generator(prompt, max_length=1000, do_sample=True)
        return results[0]["generated_text"]
