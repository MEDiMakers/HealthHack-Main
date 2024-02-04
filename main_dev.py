import shutil
import torch
from time import strftime
import os, sys, time
from argparse import ArgumentParser
from classes import User

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.utils.preprocess import CropAndExtract
from src.test_audio2coeff import Audio2Coeff
from src.facerender.animate import AnimateFromCoeff
from src.generate_batch import get_data
from src.generate_facerender_batch import get_facerender_data
from src.utils.init_path import init_path
from TTS.api import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"
from lingua import Language, LanguageDetectorBuilder
import tempfile
from llm_script import summary_adapt_llm, medicine_llm

## whatever translation feature we add here


## Audio Translation Feature
def get_audio(user, translate=False):
    languages = []
    if translate:
        main_text = user.get_translated_text()
    else:
        main_text = user.get_og_text()

    for l, v in list(user.supported_languages.values()):
        languages.append(l)

    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    confidence_values = detector.compute_language_confidence_values(main_text)
    max_val = confidence_values[0].language.name
    if max_val == "CHINESE" or max_val == "ENGLISH":
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    else:
        tts = TTS(f"tts_models/{user.supported_languages[max_val][1]}/fairseq/vits")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    # wav = tts.tts(text = main_text,speaker_wav = user.ref_audio,language= user.supported_languages[max_val][1])
    print("Audio generated!")
    print(
        max_val.lower()
        + " detected with confidence of "
        + str(confidence_values[0].value)
        + f"\n Output File path: {max_val}.wav"
    )
    tts.tts_to_file(
        text=main_text,
        speaker_wav=user.ref_audio,
        language=user.supported_languages[max_val][1],
        file_path=temp_file,
    )
    return temp_file.name


## Video Head Generation Feature (Been looking at Lipsync too but unsure)
def head_generation(user):

    # same idea from inference.py , instead we are storing it in user class
    pic_path = user.ref_img
    audio_path = user.audio
    save_dir = os.path.join(user.dir, strftime("%Y_%m_%d_%H.%M.%S"))
    os.makedirs(save_dir, exist_ok=True)
    pose_style = user.pose_style
    device = user.device
    batch_size = user.batch_size
    input_yaw_list = user.input_yaw
    input_pitch_list = user.input_pitch
    input_roll_list = user.input_roll
    ref_eyeblink = None
    ref_pose = None

    current_root_path = os.path.split(sys.argv[0])[0]

    sadtalker_paths = init_path(
        user.checkpoint_dir,
        os.path.join(current_root_path, "src/config"),
        user.size,
        user.old_version,
        user.preprocess,
    )

    # init model
    preprocess_model = CropAndExtract(sadtalker_paths, device)

    audio_to_coeff = Audio2Coeff(sadtalker_paths, device)

    animate_from_coeff = AnimateFromCoeff(sadtalker_paths, device)

    # crop image and extract 3dmm from image
    first_frame_dir = os.path.join(save_dir, "first_frame_dir")
    os.makedirs(first_frame_dir, exist_ok=True)
    print("3DMM Extraction for source image")
    first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(
        pic_path,
        first_frame_dir,
        user.preprocess,
        source_image_flag=True,
        pic_size=user.size,
    )
    if first_coeff_path is None:
        print("Can't get the coeffs of the input")
        return

    if ref_eyeblink is not None:
        ref_eyeblink_videoname = os.path.splitext(os.path.split(ref_eyeblink)[-1])[0]
        ref_eyeblink_frame_dir = os.path.join(save_dir, ref_eyeblink_videoname)
        os.makedirs(ref_eyeblink_frame_dir, exist_ok=True)
        print("3DMM Extraction for the reference video providing eye blinking")
        ref_eyeblink_coeff_path, _, _ = preprocess_model.generate(
            ref_eyeblink,
            ref_eyeblink_frame_dir,
            user.preprocess,
            source_image_flag=False,
        )
    else:
        ref_eyeblink_coeff_path = None

    if ref_pose is not None:
        if ref_pose == ref_eyeblink:
            ref_pose_coeff_path = ref_eyeblink_coeff_path
        else:
            ref_pose_videoname = os.path.splitext(os.path.split(ref_pose)[-1])[0]
            ref_pose_frame_dir = os.path.join(save_dir, ref_pose_videoname)
            os.makedirs(ref_pose_frame_dir, exist_ok=True)
            print("3DMM Extraction for the reference video providing pose")
            ref_pose_coeff_path, _, _ = preprocess_model.generate(
                ref_pose, ref_pose_frame_dir, user.preprocess, source_image_flag=False
            )
    else:
        ref_pose_coeff_path = None

    # audio2ceoff
    batch = get_data(
        first_coeff_path, audio_path, device, ref_eyeblink_coeff_path, still=user.still
    )
    coeff_path = audio_to_coeff.generate(
        batch, save_dir, pose_style, ref_pose_coeff_path
    )

    # 3dface render # unless we want a composed video, else don't need
    #  if user.face3dvis:
    #   from src.face3d.visualize import gen_composed_video
    ##
    #   gen_composed_video(user, device, first_coeff_path, coeff_path, audio_path, os.path.join(save_dir, '3dface.mp4'))

    # coeff2video
    data = get_facerender_data(
        coeff_path,
        crop_pic_path,
        first_coeff_path,
        audio_path,
        batch_size,
        input_yaw_list,
        input_pitch_list,
        input_roll_list,
        expression_scale=user.expression_scale,
        still_mode=user.still,
        preprocess=user.preprocess,
        size=user.size,
    )

    result = animate_from_coeff.generate(
        data,
        save_dir,
        pic_path,
        crop_info,
        enhancer=user.enhancer,
        background_enhancer=user.background_enhancer,
        preprocess=user.preprocess,
        img_size=user.size,
    )

    shutil.move(result, save_dir + ".mp4")
    print("The generated video is named:", save_dir + ".mp4")


import soundfile as sf
import librosa


def main(
    text, ref_audio, ref_img, save_dir="./results", lang="ENGLISH", translate=False
):
    main_init = User(text, ref_audio, ref_img, save_dir, lang, translate)

    # 1: Translate  (Embedded within class)

    # 2: Audio Translate
    temp_name = get_audio(main_init)
    data, samplerate = sf.read(temp_name)
    wav = librosa.resample(data, orig_sr=samplerate, target_sr=16000)

    resampled_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    # standard wave
    sf.write(resampled_file, wav, 16000)
    main_init.audio = resampled_file.name

    # 3: Head Generation
    # TO DO: Settle the Talking Path folder
    # head_generation(main_init)


# sys.path.append(os.path.join(os.path.dirname(__file__),'dev'))
# test_prompt1 = """Medical Report:
# History: The patient is a 44-year-old male presenting with a two-week history of intermittent chest pain and shortness of breath. He reports the pain is more pronounced during physical activity and alleviates upon rest. There is a family history of coronary artery disease.

# Physical Examination: On examination, the patient appeared in moderate distress. Vital signs were within normal limits. Cardiac auscultation revealed no murmurs, rubs, or gallops. Lungs were clear to auscultation bilaterally. Abdominal examination was unremarkable.

# Investigations:
# - Electrocardiogram (ECG) showed no evidence of acute ischemia but indicated inverted T waves in the lateral leads.
# - Chest X-ray was clear with no signs of congestion.
# - Blood tests indicated slightly elevated cholesterol levels.

# Impression: The clinical presentation and investigations suggest stable angina. The ECG findings, while not indicative of acute ischemia, warrant further evaluation with a stress test and possibly a coronary angiography, considering the family history of coronary artery disease.

# Recommendations:
# - Initiate treatment with beta-blockers and statin therapy.
# - Schedule for a stress test and follow-up consultation.
# - Advise lifestyle modifications including a low-cholesterol diet and regular exercise.
# - Patient should seek immediate medical attention if symptoms worsen or new symptoms arise."""


input_text = """Patient Name: John Doe  \n
            Date of Birth: 01/01/1980  \n
            Date of Examination: 01/20/2024 \n
            Referring Physician: Dr. Jane Smith \n
            Medical Report: \n
            History: The patient is a 44-year-old male presenting with a two-week history of intermittent chest pain and shortness of breath. He reports the pain is more pronounced during physical activity and alleviates upon rest. There is a family history of coronary artery disease. \n
            Physical Examination: On examination, the patient appeared in moderate distress. Vital signs were within normal limits. Cardiac auscultation revealed no murmurs, rubs, or gallops. Lungs were clear to auscultation bilaterally. Abdominal examination was unremarkable. \n
            Investigations: \n
            - Electrocardiogram (ECG) showed no evidence of acute ischemia but indicated inverted T waves in the lateral leads. \n
            - Chest X-ray was clear with no signs of congestion. \n
            - Blood tests indicated slightly elevated cholesterol levels. \n

            Impression: The clinical presentation and investigations suggest stable angina. The ECG findings, while not indicative of acute ischemia, warrant further evaluation with a stress test and possibly a coronary angiography, considering the family history of coronary artery disease. \n
            Recommendations: \n
            - Initiate treatment with beta-blockers and statin therapy. \n
            - Schedule for a stress test and follow-up consultation. \n
            - Advise lifestyle modifications including a low-cholesterol diet and regular exercise. \n
            - Patient should seek immediate medical attention if symptoms worsen or new symptoms arise. \n """

test_prompt1 = input_text
# model_1 = "Falconsai/medical_summarization"
# model_2 = "TheBloke/medicine-chat-GGUF"
ref_audio = r"D:\NUS\Hackathon\HealthHack\dev\references\audio\converted.wav"
ref_img = r"D:\NUS\Hackathon\HealthHack\dev\references\images\doctor.jpg"
save_dir = "./results"
_text = medicine_llm(test_prompt1)  # model_type= model_2)
main(_text, ref_audio, ref_img, save_dir)
