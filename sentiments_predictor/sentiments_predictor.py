import torch

from transformers import BertTokenizer, BertForSequenceClassification

class SentimentsPredictor:
    def __init__(self, max_length: int=512):
        self.max_length = max_length
        self.tokenizer = BertTokenizer.from_pretrained('thu-coai/roberta-base-cold')
        self.model = BertForSequenceClassification.from_pretrained('thu-coai/roberta-base-cold')
        self.model.eval()

    def predict(self, text: str):
        if not isinstance(text, str):
            return -99
        text = text.strip()
        if len(text) == 0 or text == '-99':
            return -99
        tokenized_text = self.tokenizer(text, truncation=True, max_length=self.max_length)
        model_input = {key: torch.tensor(val).unsqueeze(0) for key, val in tokenized_text.items()}
        model_output = self.model(**model_input, return_dict=False)
        prediction = torch.argmax(model_output[0].cpu(), dim=-1)
        return prediction.item() if prediction is not None else -99

if __name__ == '__main__':
    import fire
    fire.Fire(SentimentsPredictor())
