from pathlib import Path
import re

def parse_qa(file):
    with open(file) as qa_file:
        qa_content = qa_file.read()
    qas = qa_content.split('QUES')
    for qai in qas[1:]:
        qsn = re.search(r'\d+\.(.*)\n\(a\)', qai, re.DOTALL)
        print(qsn.group(1))
        ansrs = re.findall(r'\([abcde]\)(.*)', qai)
        print(ansrs)
        corr_ans = re.search('उत्तर.*\(([abcde])\)', qai)
        print(corr_ans.group(1))
        # print(qsn, ansrs, corr_ans)
        # print("\nQuestion:", qsn, "\n\nPossible answers:\n", "\n".join(ansrs), "\n\nCorrect answer: ", corr_ans)


if __name__ == '__main__':
    current_dir = Path(__file__).parent
    # print(current_dir)
    parse_qa(current_dir.joinpath('10.txt'))