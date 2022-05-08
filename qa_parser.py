from pathlib import Path

def parse_qa(file):
    with open(file) as qa_file:
        qa_content = qa_file.read()
    qas = qa_content.split('QUES')
    for qa in qas[1:]:
        qa = qa.split('\n')
        # print(qa)
        qsn = qa[0]
        ansrs = qa[2:6]
        corr_ans = qa[7].split('-')[-1]
        # print(qsn, ansrs, corr_ans)
        print("\nQuestion:", qsn, "\n\nPossible answers:\n", "\n".join(ansrs), "\n\nCorrect answer: ", corr_ans)


if __name__ == '__main__':
    current_dir = Path(__file__).parent
    # print(current_dir)
    parse_qa(current_dir.joinpath('10.txt'))