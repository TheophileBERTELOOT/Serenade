import librosa
import numpy as np
import os
import matplotlib.pyplot as plt

class DataTransformer:
    def __init__(self):
        pass
    
    def load_and_pad_audio(self,file_path, target_duration=10, sr=22050):
        y, _ = librosa.load(file_path, sr=sr)
        max_length = int(sr * target_duration)
        if len(y) > max_length:
            y = y[:max_length]
        else:
            y = np.pad(y, (0, max_length - len(y)))
        return y
    
    def audio_to_mel_spectrogram(self,file_path, n_mels=128, duration=10, sr=22050):
        y = self.load_and_pad_audio(file_path, target_duration=duration, sr=sr)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)  # Convertir en dB
        return mel_spec_db
    
    def visualize_spectrogram(self,mel_spec, sr=22050, hop_length=512):
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(mel_spec, sr=sr, hop_length=hop_length, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel Spectrogram')
        plt.tight_layout()
        plt.show()
        
    def save_as_image(self,mel_spec_db, output_path):
        plt.figure(figsize=(10, 4))
        plt.axis('off')  # Supprimer les axes
        plt.imshow(mel_spec_db, aspect='auto', origin='lower', cmap='viridis')  # Spectrogramme en couleurs
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, format='png')  # Sauvegarder en PNG
        plt.close()
        
    def transformData(self):
        audioDirectory = "serenade/Dataset/Data/audios/"
        audiosFolders = [f for f in os.listdir(audioDirectory) if os.path.isdir(os.path.join(audioDirectory, f))]
        imgsDirectory = "serenade/Dataset/Data/imgs/"
        imgsFolders = [f for f in os.listdir(imgsDirectory) if os.path.isdir(os.path.join(imgsDirectory, f))]
        
        for audioFolder in audiosFolders:
            if not audioFolder in imgsFolders:
                imgDirectory = imgsDirectory+audioFolder+'/'
                os.makedirs(imgsDirectory+audioFolder)
                audiosFiles = [f for f in os.listdir(audioDirectory+audioFolder)]
                for audioFile in audiosFiles:
                    spectro = self.audio_to_mel_spectrogram(audioDirectory+audioFolder+'/'+audioFile)
                    self.save_as_image(spectro,imgDirectory+audioFile.split('.')[0]+'.png')
                    # if audioFile == audiosFiles[0]:
                    #     self.visualize_spectrogram(spectro)
                 
            
        