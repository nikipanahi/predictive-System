from rapidfuzz import process, fuzz
import random

# --- تنظیمات اولیه ---
standard_parts = ["Engine Valve", "Landing Gear System", "Hydraulic Pump", "Turbine Blade"]
qwerty_map = {
    'q': 'wase', 'w': 'qeasd', 'e': 'wrsfd', 'r': 'etdfg', 't': 'ryfgh', 'y': 'tughj', 'u': 'yihjk', 'i': 'uojkl', 'o': 'ipkl', 'p': 'ol',
    'a': 'qwsxz', 's': 'qweadzx', 'd': 'ersfcx', 'f': 'rtdgcv', 'g': 'tyfhvb', 'h': 'yugjbn', 'j': 'uihknm', 'k': 'uijlm', 'l': 'okp',
    'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
}

# تابع تولید نویز (همان که قبلاً نوشتیم)
def inject_typo(word, prob=0.3):
    if random.random() > prob: return word
    word_list = list(word)
    idx = random.choice([i for i, c in enumerate(word_list) if c.isalpha()])
    error_type = random.choice(['sub', 'del', 'trans'])
    if error_type == 'sub' and word_list[idx].lower() in qwerty_map:
        word_list[idx] = random.choice(qwerty_map[word_list[idx].lower()])
    elif error_type == 'del' and len(word_list) > 3:
        word_list.pop(idx)
    elif error_type == 'trans' and idx < len(word_list) - 1:
        word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]
    return "".join(word_list)

# --- مرحله اصلی تست ---
dataset_size = 1000
raw_data = [random.choice(standard_parts) for _ in range(dataset_size)]
noisy_data = [inject_typo(item, prob=0.2) for item in raw_data] # با احتمال ۲۰٪ خطا وارد کن

# ارزیابی
total_correct = 0
for i in range(dataset_size):
    original = raw_data[i]
    noisy = noisy_data[i]
    
    # اینجا سیستم فازی تو وارد عمل می‌شود
    best_match = process.extractOne(noisy, standard_parts, scorer=fuzz.WRatio)
    if best_match[0] == original:
        total_correct += 1

# گزارش نهایی
accuracy = (total_correct / dataset_size) * 100
print(f"نتایج تست دقت الگوریتم فازی:")
print(f"تعداد کل لاگ‌ها: {dataset_size}")
print(f"دقت سیستم در بازیابی داده‌های صحیح: {accuracy:.2f}%")