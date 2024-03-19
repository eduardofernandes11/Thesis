import torch
from transformers import AutoModelForSequenceClassification

class RobertaEmotionsClass(torch.nn.Module):
    def __init__(self, model_name):
        super(RobertaEmotionsClass, self).__init__()
        self.l1 = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pre_classifier = torch.nn.Linear(768, 768)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768, 28)

    def forward(self, input_ids, attention_mask, token_type_ids):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        return output_1.logits