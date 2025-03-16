import pytorch_lightning as pl
import torch
import torch.nn as nn
import torch.nn.functional as F


class AudioDataModule(pl.LightningDataModule):
    def __init__(self, train_spectrograms, train_labels, val_spectrograms, val_labels, batch_size=32):
        super().__init__()
        self.train_spectrograms = train_spectrograms
        self.train_labels = train_labels
        self.val_spectrograms = val_spectrograms
        self.val_labels = val_labels
        self.batch_size = batch_size

    def setup(self, stage=None):
        self.train_dataset = SpectrogramDataset(self.train_spectrograms, self.train_labels)
        self.val_dataset = SpectrogramDataset(self.val_spectrograms, self.val_labels)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False)
    
    
#-------------------------------MODEL-------------------------------------------------
    
class AudioClassifier(pl.LightningModule):
    def __init__(self, num_classes):
        super(AudioClassifier, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 32 * 32, 128)  # Ajustez selon la taille après convolutions
        self.fc2 = nn.Linear(128, num_classes)
        self.dropout = nn.Dropout(0.5)

        self.criterion = nn.CrossEntropyLoss()

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)  # Flatten
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.forward(x)
        loss = self.criterion(y_hat, y)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.forward(x)
        loss = self.criterion(y_hat, y)
        acc = (y_hat.argmax(dim=1) == y).float().mean()
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", acc, prog_bar=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.001)