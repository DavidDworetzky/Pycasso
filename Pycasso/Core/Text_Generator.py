import argparse
import logging
from tqdm import trange

import torch
import torch.nn.functional as F
import numpy as np

from pytorch_pretrained_bert import GPT2LMHeadModel, GPT2Tokenizer

def top_k_logits(logits, k):
    """
    Masks everything but the k top entries as -infinity (1e10).
    Used to mask logits such that e^-infinity -> 0 won't contribute to the
    sum of the denominator.
    """
    if k == 0:
        return logits
    else:
        values = torch.topk(logits, k)[0]
        batch_mins = values[:, -1].view(-1, 1).expand_as(logits)
        return torch.where(logits < batch_mins, torch.ones_like(logits) * -1e10, logits)

def sample_sequence(model, length, start_token=None, batch_size=None, context=None, temperature=1, top_k=0, device='cuda', sample=True):
    if start_token is None:
        assert context is not None, 'Specify exactly one of start_token and context!'
        context = torch.tensor(context, device=device, dtype=torch.long).unsqueeze(0).repeat(batch_size, 1)
    else:
        assert context is None, 'Specify exactly one of start_token and context!'
        context = torch.full((batch_size, 1), start_token, device=device, dtype=torch.long)
    prev = context
    output = context
    past = None
    with torch.no_grad():
        for i in trange(length):
            logits, past = model(prev, past=past)
            logits = logits[:, -1, :] / temperature
            logits = top_k_logits(logits, k=top_k)
            log_probs = F.softmax(logits, dim=-1)
            if sample:
                prev = torch.multinomial(log_probs, num_samples=1)
            else:
                _, prev = torch.topk(log_probs, k=1, dim=-1)
            output = torch.cat((output, prev), dim=1)
    return output

class Text_Generator:
    def __init__(self, text_sequence, model_type, temperature = 1.0, top_k = 0, batch_size = 1, length = 1, nsamples =1, debug = True):
        self.text_sequence = text_sequence
        #eventually will differentiate between gpt-2, BERT, etc.
        self.model_type = model_type
        model_name = 'gpt2'
        self.debug = debug
        #detect device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.temperature = temperature
        self.top_k = top_k
        self.batch_size = batch_size
        self.length = length
        self.nsamples = nsamples
        #create encoder and model
        self.enc = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        
    def generate_text(self, batch_size):
        context_tokens = []
        raw_text = self.text_sequence
        context_tokens = self.enc.encode(raw_text)
        generated = 0
        for _ in range(self.nsamples // self.batch_size):
            out = sample_sequence(
                model=self.model, length=self.length,
                context=context_tokens,
                start_token=None,
                batch_size=self.batch_size,
                temperature=self.temperature, top_k=self.top_k, device=self.device
            )
            out = out[:, len(context_tokens):].tolist()
            for i in range(self.batch_size):
                generated += 1
                text = self.enc.decode(out[i])
        return text
