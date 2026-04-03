# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 12:57:38 2024

See LICENSE file in the root of the repository. 

Copyright (c) Aki Härmä, DACS/FSE, Maastricht University, 2023
"""

# Use a pipeline as a high-level helper
from transformers import pipeline
import torchaudio as ta
import torch
import soundfile
# Load model directly
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def read_soundfile(fname):
    sig, f = soundfile.read(str(fname))
    return torch.DoubleTensor(sig.T), f

class MIT_AST_model():
    def __init__(self):
        # self.pipe = pipeline("audio-classification", model="MIT/ast-finetuned-audioset-10-10-0.4593")
        self.extractor = AutoFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-14-14-0.443")
        self.model = AutoModelForAudioClassification.from_pretrained("MIT/ast-finetuned-audioset-14-14-0.443")
        self.model.to(DEVICE)
    def classify(self, audio_file):
        sig, fs = read_soundfile(audio_file)
        sig16 = ta.transforms.Resample(orig_freq=fs,new_freq=16000)(sig[0,:].type(torch.float32))
        inputs = self.extractor(sig16, sampling_rate=16000, return_tensors="pt")        
        with torch.no_grad():
            logits = self.model(**inputs.to(DEVICE)).logits

        predicted_class_ids = torch.argmax(logits, dim=-1).item()
        predicted_label = self.model.config.id2label[predicted_class_ids]
        return predicted_label

# classifier = MIT_AST_model()
# afile = "../gardenTransformer/data/samples/bluetit_1.wav"

# res = classifier.classify(afile)



