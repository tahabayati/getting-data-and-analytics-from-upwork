# یک فولدر به اسم freelancer و یک فولدر به اسم employer در کنار این فایل ایجاد کنید
#از طریق افزونه کروم Instant Data Scraper داده های خود را از سایت upwork استخراج کنید
# سپس کد را ران کرده و اسمی که برای بالای عکس و نام فولدر و فایل ها میخواهید را وارد کنید
# خود اسم اسکیلی که سرچ کردین و داخل نتیجه گذاشته نمیشه
# 
import pandas as pd
from collections import Counter
import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

class UpworkDataProcessor:
    def __init__(self, chart_title="Skills Analysis", filename="skills"):
        self.freelancer_skills = Counter()
        self.employer_skills = Counter()
        self.chart_title = chart_title
        self.filename = filename
        self.result_dir = Path("Result")
        self.output_dir = self.result_dir / filename
        self._ensure_directories()
        plt.style.use('default')
        sns.set_theme()
        self.title_keywords = [word.lower().strip() for word in chart_title.split()]

    def _ensure_directories(self):
        self.result_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def process_directory(self, directory_path, is_freelancer=True):
        try:
            csv_files = list(Path(directory_path).glob('*.csv'))
            for csv_file in csv_files:
                self.process_csv_data(csv_file, is_freelancer)
        except Exception:
            pass

    def process_csv_data(self, csv_file_path, is_freelancer=True):
        try:
            df = pd.read_csv(csv_file_path)
            token_columns = [col for col in df.columns if 'air3-token' in col]
            highlight_columns = [col for col in df.columns if col in ['highlight', 'highlight-color']]
            all_columns = token_columns + highlight_columns
            
            for column in all_columns:
                skills = df[column].dropna().values
                filtered_skills = [
                    skill for skill in skills 
                    if not any(keyword in str(skill).lower() for keyword in self.title_keywords)
                ]
                if is_freelancer:
                    self.freelancer_skills.update(filtered_skills)
                else:
                    self.employer_skills.update(filtered_skills)
        except Exception:
            pass

    def create_visualization(self, sorted_skills, top_n=20):
        try:
            top_skills = sorted_skills[:top_n]
            plt.figure(figsize=(15, 10), dpi=100)
            
            skills = [skill for skill, _, _, _ in top_skills]
            freelancer_counts = [f_count for _, f_count, _, _ in top_skills]
            employer_counts = [e_count for _, _, e_count, _ in top_skills]
            
            x = range(len(skills))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], freelancer_counts, width, 
                   label='Freelancers', color=sns.color_palette()[0], alpha=0.8)
            plt.bar([i + width/2 for i in x], employer_counts, width, 
                   label='Employers', color=sns.color_palette()[1], alpha=0.8)
            
            plt.grid(True, alpha=0.3)

            plt.xticks(x, skills, rotation=45, ha='right')
            plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
            plt.title(f'{self.chart_title}', 
                     fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()
            
            output_path = self.output_dir / f'{self.filename}.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close()
        except Exception:
            pass

    def save_results(self):
        try:
            all_skills = set(self.freelancer_skills.keys()) | set(self.employer_skills.keys())
            sorted_skills = [(
                skill,
                self.freelancer_skills[skill],
                self.employer_skills[skill],
                self.freelancer_skills[skill] + self.employer_skills[skill]
            ) for skill in all_skills]
            
            sorted_skills.sort(key=lambda x: x[3], reverse=True)
            
            output_path = self.output_dir / f'{self.filename}.csv'
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Skill', 'Freelancer Count', 'Employer Count', 'Total'])
                for skill_data in sorted_skills:
                    if str(skill_data[0]).strip():
                        writer.writerow(skill_data)
            
            self.create_visualization(sorted_skills)
        except Exception:
            pass

def main():
    chart_title = input("Enter chart title: ").strip()
    filename = input("Enter filename: ").strip()
    processor = UpworkDataProcessor(chart_title, filename)
    
    freelancer_dir = Path("freelancer")
    if freelancer_dir.exists():
        processor.process_directory(freelancer_dir, is_freelancer=True)
    
    employer_dir = Path("employer")
    if employer_dir.exists():
        processor.process_directory(employer_dir, is_freelancer=False)
    
    processor.save_results()

if __name__ == "__main__":
    main()
