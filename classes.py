import shutil
from lingua import Language
import torch

class R50: # ResNet50 Initializer
    def __init__(self) -> None:
        self.net_recon = 'resnet50'
        self.init_path = None # useless
        self.use_last_fc = False 
        self.bfm_folder = './checkpoints/BFM_Fitting/'
        self.bfm_model = 'BFM_model_front.mat'

class HeadGeneration: # Main Head Generation Args
    def __init__(self) -> None: 
        # head generation checkpoint
        self.checkpoint_dir = "./checkpoints/hub/checkpoints" # checkpoint directory
        #self.dir = None

        # for head generation (head generation functions) => it will be set below
        self.pose_style = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ref_eyeblink = None
        self.ref_pose = None
        self.expression_scale = 1
        self.input_yaw = None
        self.input_pitch = None
        self.input_roll = None
        self.enhancer = None
        self.background_enhancer = None
        self.batch_size = 2
        self.pose_style = 0
        self.size = 256
        self.preprocess = 'crop'
        self.face3dvis = True
        self.still = True
        self.verbose = True
        self.old_version = False


        #Rendering Parameters
       # self.focal = 1015.
       # self.center = 112.
       # self.camera_d = 10.
       # self.z_near = 5.
       # self.z_far = 15.
class User(HeadGeneration,R50):
    def __init__(self,text,ref_audio,ref_img,save_dir,lang = 'ENGLISH',translate = False):
        super().__init__()
        self.dir = save_dir
        self.original_text = text
        self.supported_languages = {'ENGLISH': [Language.ENGLISH,"en"],'CHINESE': [Language.CHINESE,"zh-cn"],'MALAY': [Language.MALAY,"zlm"],'TAMIL': [Language.TAMIL,"tam"]}
        self.translated_text = self.translate(lang)
        self.ref_audio = ref_audio
        self.audio = None # we store the translated audio here
        self.ref_img = ref_img
        self.final_video = None # we store the final video here

    def get_ref_audio(self):
        return self.ref_audio
    def get_ref_img(self):
        return self.ref_img
    def get_og_text(self):
        return self.original_text
    def get_translated_text(self):
        return self.translated_text
    def get_supported_languages(self):
        print(f"We only support " + str(list(self.supported_languages.keys())))
        
    # to perform a translated option:: (Probably thru Google or something open source idk)
    def translate(self,lang):
        if lang in list(self.supported_languages.keys()):
            ## do the language translation option here
            return self.original_text
        
        else:
            print("We only support the following languages: English , Chinese , Malay , Tamil")
            return self.original_text
        
        
    def change_final_video(self,video):
        self.final_video = video
        return "Final Video Done!"

    def save_final_video(self,path):
        shutil.move(self.final_video,path + '.mp4')
        print('The generated video is named:', path+'.mp4')
        