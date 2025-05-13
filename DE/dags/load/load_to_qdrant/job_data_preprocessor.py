import pandas as pd
import json
import os
import re
from translator import VietnameseTranslator
import asyncio



class JobDataMapperAndTranslator:
    def __init__(self, df: pd.DataFrame, translator=VietnameseTranslator()):
        self.df = df.copy()
        self.translator = translator
        self.province_translation = {
            'An Giang': 'An Giang', 'Bà Rịa-Vũng Tàu': 'Ba Ria - Vung Tau', 'Bạc Liêu': 'Bac Lieu',
            'Bắc Giang': 'Bac Giang', 'Bắc Kạn': 'Bac Kan', 'Bắc Ninh': 'Bac Ninh',
            'Bến Tre': 'Ben Tre', 'Bình Dương': 'Binh Duong', 'Bình Định': 'Binh Dinh',
            'Bình Phước': 'Binh Phuoc', 'Bình Thuận': 'Binh Thuan', 'Cà Mau': 'Ca Mau',
            'Cao Bằng': 'Cao Bang', 'Cần Thơ': 'Can Tho', 'Đà Nẵng': 'Da Nang',
            'Đắk Lắk': 'Dak Lak', 'Đắk Nông': 'Dak Nong', 'Điện Biên': 'Dien Bien',
            'Đồng Nai': 'Dong Nai', 'Đồng Tháp': 'Dong Thap', 'Gia Lai': 'Gia Lai',
            'Hà Giang': 'Ha Giang', 'Hà Nam': 'Ha Nam', 'Hà Nội': 'Hanoi',
            'Hà Tĩnh': 'Ha Tinh', 'Hải Dương': 'Hai Duong', 'Hải Phòng': 'Hai Phong',
            'Hậu Giang': 'Hau Giang', 'Hòa Bình': 'Hoa Binh', 'Hưng Yên': 'Hung Yen',
            'Khánh Hòa': 'Khanh Hoa', 'Kiên Giang': 'Kien Giang', 'Kon Tum': 'Kon Tum',
            'Lai Châu': 'Lai Chau', 'Lâm Đồng': 'Lam Dong', 'Lạng Sơn': 'Lang Son',
            'Lào Cai': 'Lao Cai', 'Long An': 'Long An', 'Nam Định': 'Nam Dinh',
            'Nghệ An': 'Nghe An', 'Ninh Bình': 'Ninh Binh', 'Ninh Thuận': 'Ninh Thuan',
            'Phú Thọ': 'Phu Tho', 'Phú Yên': 'Phu Yen', 'Quảng Bình': 'Quang Binh',
            'Quảng Nam': 'Quang Nam', 'Quảng Ngãi': 'Quang Ngai', 'Quảng Ninh': 'Quang Ninh',
            'Quảng Trị': 'Quang Tri', 'Sóc Trăng': 'Soc Trang', 'Sơn La': 'Son La',
            'Tây Ninh': 'Tay Ninh', 'Thái Bình': 'Thai Binh', 'Thái Nguyên': 'Thai Nguyen',
            'Thanh Hóa': 'Thanh Hoa', 'Thừa Thiên-Huế': 'Thua Thien - Hue', 'Tiền Giang': 'Tien Giang',
            'Trà Vinh': 'Tra Vinh', 'Tuyên Quang': 'Tuyen Quang', 'Vĩnh Long': 'Vinh Long',
            'Vĩnh Phúc': 'Vinh Phuc', 'Yên Bái': 'Yen Bai', 'Hồ Chí Minh': 'Ho Chi Minh City',
            "ha noi": "Hanoi", 'ho chi minh city, ho chi minh city, vietnam': 'Ho Chi Minh City',
            'hanoi, hanoi, vietnam': 'Hanoi', 'ho chi minh city, vietnam': 'Ho Chi Minh City',
            'hà nội, hn, vn': 'Hanoi', 'vn': 'Viet Nam'
        }
        self.normalized_provinces = {
            k.lower().strip(): v for k, v in self.province_translation.items()}

    def map_all(self):
        self.map_job_level()
        self.map_location()
        self.map_job_type()
        return self.df

    def map_job_level(self):
        def normalize_job_level(level):
            if not isinstance(level, str):
                return "Unknown"
            level = level.lower().strip()
            mapping = {
                "intern": "Intern", "student": "Intern", "thực tập sinh": "Intern",
                "entry": "Entry-Level", "fresher": "Entry-Level",
                "junior": "Junior", "intermediate": "Mid-Level", "middle": "Mid-Level",
                "mid": "Mid-Level", "mid-level": "Mid-Level", "mid level": "Mid-Level",
                "mid-senior level": "Senior", "senior": "Senior",
                "lead": "Lead", "teamlead": "Lead", "tech lead": "Lead", "technical lead": "Lead",
                "principal": "Lead", "manager": "Manager", "project manager": "Manager",
                "senior manager": "Manager", "associate manager": "Manager",
                "director": "Director", "c-level": "C-Level", "cto": "C-Level",
                "chief technology officer": "C-Level", "vp": "C-Level", "vice president": "C-Level",
                "avp": "C-Level", "executive": "Executive", "staff": "Staff",
                "engineer": "Engineer", "developer": "Engineer", "scientist": "Engineer",
                "qa": "Engineer", "tester": "Engineer", "architect": "Lead",
                "consultant": "Professional", "specialist": "Professional", "professional": "Professional",
                "coordinator": "Professional", "analyst": "Professional",
                "freelancer": "Other",
            }
            for keyword, mapped in mapping.items():
                if keyword in level:
                    return mapped
            return "Unknown"

        self.df["normalized_job_level"] = self.df["job_level"].astype(
            str).str.lower().str.strip()
        self.df["mapped_level"] = self.df["normalized_job_level"].apply(
            normalize_job_level)

    def map_location(self):
        def extract_province(location):
            if not isinstance(location, str) or not location.strip():
                return "Unknown"
            location_lower = location.lower()
            for norm_province, eng_province in self.normalized_provinces.items():
                if norm_province in location_lower:
                    return eng_province
            return "Other"

        self.df["normalized_location"] = self.df["location"].astype(
            str).str.lower().str.strip()
        self.df["mapped_location"] = self.df["location"].apply(
            extract_province)

    def map_job_type(self):
        def map_job_type(job_type):
            if not isinstance(job_type, str) or not job_type.strip():
                return "Unknown"
            job_type = job_type.lower()
            if 'contract' in job_type:
                return 'Contract'
            elif 'internship' in job_type:
                return 'Internship'
            elif 'fulltime' in job_type:
                return 'Full-Time'
            elif 'parttime' in job_type:
                return 'Part-Time'
            elif 'temporary' in job_type:
                return 'Temporary'
            else:
                return 'Other'

        self.df["mapped_job_type"] = self.df["job_type"].apply(map_job_type)

    async def process_row(self, index, row):
        qs_text = row.get("qualifications & skills", "")
        responsibilities_text = row.get("responsibilities", "")
        description_text = row.get("description", "")

        qs_translated = await self.translator.translate_if_vietnamese(qs_text if isinstance(qs_text, str) else "")
        responsibilities_translated = await self.translator.translate_if_vietnamese(responsibilities_text if isinstance(responsibilities_text, str) else "")

        if isinstance(description_text, str) and len(description_text) <= 1500:
            description_translated = await self.translator.translate_if_vietnamese(description_text)
        else:
            description_translated = ""

        if description_translated:
            merge_text = rf"""
Title: {row.get("title", "")}
Job level: {row.get("job_level", "")}
Working type: {row.get("job_type", "")}
Company: {row.get("company", "")}

Description: {description_translated}

Qualifications & Skills:
{qs_translated}

Responsibilities:
{responsibilities_translated}
            """.strip()
        else:
            merge_text = rf"""
Title: {row.get("title", "")}
Job level: {row.get("job_level", "")}
Working type: {row.get("job_type", "")}
Company: {row.get("company", "")}

Qualifications & Skills:
{qs_translated}

Responsibilities:
{responsibilities_translated}
            """.strip()

        return merge_text

    async def generate_merged_texts(self):
        tasks = [self.process_row(idx, row) for idx, row in self.df.iterrows()]
        merge_text = await asyncio.gather(*tasks)
        self.df["merge_input"] = merge_text

    async def run(self):
        self.map_all()
        await self.generate_merged_texts()
        return self.df
