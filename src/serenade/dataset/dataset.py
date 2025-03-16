from PIL import Image
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, Dataset


class SpectrogramDataset(Dataset):
    def __init__(self, spectrograms, labels):
        self.spectrograms = spectrograms
        self.label_encoder = LabelEncoder()
        self.labelsNames = labels
        self.labels = label_encoder.fit_transform(labels)

    def __len__(self):
        return len(self.spectrograms)

    def __getitem__(self, idx):
        spectrogram = self.spectrograms[idx]
        label = self.labels[idx]
        return torch.tensor(spectrogram, dtype=torch.float32).unsqueeze(0), torch.tensor(label, dtype=torch.long)
