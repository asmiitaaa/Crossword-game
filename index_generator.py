with open("2of12.txt") as f:
    words = [line.strip().upper() for line in f if len(line.strip()) >= 3]
#words- has all the words in our wordlist 


#the index stores all the words by the length of the word
def build_length_index(words):
    index={}
    for word in words: 
        length=len(word)
        #if the length of the word is not in the index, we add that key to the index
        if length not in index:
            index[length]=[]
        index[length].append(word)
    return index

def matches(pattern, length_index):
    result = []
    candidates = length_index.get(len(pattern), [])
    #it gets from length index where the key is len(patter), otherwise empty list
    for word in candidates:
        ok = True
        for i in range(len(pattern)):
            #we have the pattern, we have to fill that pattern with an appropriate word from the candidates
            if pattern[i] != '_' and pattern[i] != word[i]:
                ok = False#this position breaks the pattern
                break 
        if ok:
            result.append(word)#if all the positions match
    return result


# --- test ---
if __name__ == "__main__":
    length_index = build_length_index(words)
    print(matches("_A_T_", length_index))   # expect words with A at pos 2, T at pos 4