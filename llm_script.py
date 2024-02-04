# import the generated text from ocr_word into this file to generate the summary

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
from llama_cpp import Llama

model_1 = "Falconsai/medical_summarization"
model_2 = r"D:\NUS\Hackathon\HealthHack\dev\llm\medicine-chat.Q5_K_S.gguf"
#model_2 = "AdaptLLM/medicine-LLM"

#text = 'Placeholder for text received from ocr model'


# Model types 1
def summary_falconsai(text,model_type = model_1):
    tokenizer = AutoTokenizer.from_pretrained(model_type)
    inputs = tokenizer(text, return_tensors="pt").input_ids
    
    model = AutoModelForSeq2SeqLM.from_pretrained(model_type)
    outputs = model.generate(inputs, max_new_tokens=100, do_sample=False)
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text




def summary_adapt_llm(text,model_type = model_2):
    model = AutoModelForCausalLM.from_pretrained(model_type,model_file = "medicine-chat.Q5_K_S.gguf",model_type = 'llama')
    tokenizer = AutoTokenizer.from_pretrained(model_type, use_fast=False)
    user_input = f'''Given the following medical report, provide a concise summary highlighting the key findings, 
    diagnosis, and recommendations:

    {text}
    ''' 
    
    prompt = user_input
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(1)#model.device)
    outputs = model.generate(input_ids=inputs, max_length=2048)[0]
    answer_start = int(inputs.shape[-1])
    generated_text = tokenizer.decode(outputs[answer_start:], skip_special_tokens=True)
    return generated_text



def medicine_llm(text):
    llm = Llama(
    model_path=r"D:\NUS\Hackathon\HealthHack\dev\llm\medicine-chat.Q5_K_S.gguf",  # Download the model file first
    n_ctx=4096,  # The max sequence length to use - note that longer sequence lengths require much more resources
    n_threads=8,            # The number of CPU threads to use, tailor to your system and the resulting performance
    n_gpu_layers= 22, # 20 - 24 layers
          # The number of layers to offload to GPU, if you have GPU acceleration available
    )

    system_message = """
You are a medical researcher tasked with summarizing and writing concise summaries of medical reports. 
In your responses, focus on simplifying complex medical terms and concepts. 
Aim to make your explanations easily understandable for the elderly and laypeople who may not be familiar with medical jargon.
If you are answering a question, think step by step and use plain language.
Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense or is not factually coherent, explain why instead of answering something incorrect.
If you don't know the answer, please don't share false information.
Lastly, do not generate more than 128 tokens.

"""

    output = llm(
    f"[INST] <<SYS>>\n \
    {system_message}\n \
    <</SYS>>\n{text}  \
    [/INST]", # Prompt
    max_tokens=128,  # Generate up to 512 tokens
    stop=["</s>"],   # Example stop token - not necessarily correct for this specific model! Please check before using.
    echo=False        # Whether to echo the prompt
    )

    output = output['choices'][0]['text']
    del llm # Free up resources
    return output

# if you wanna test run LLM

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

#test_prompt1 = "Medical Diagnosis on Heart Attack"
#print(medicine_llm(test_prompt1))
