"""
لعبة تنظيم حياة الطالب الأردني
Student Life Organizer Game - For Jordanian Students
النسخة المتقدمة والكاملة
Version 2.0 - Advanced Edition

المطور: Copilot
الهدف: تنظيم حياة الطالب والموازنة بين الدراسة والحياة الشخصية
Target: Help students manage their life and balance between studies and personal life
"""

import pygame
import sys
import random
import json
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math


# ==================== التعريفات والثوابت ====================

class StudentGrade(Enum):
    """تعريف مستويات الصفوف في الأردن"""
    FIRST_SECONDARY = "الأول الثانوي (Grade 10)"
    SECOND_SECONDARY = "الثاني الثانوي (Grade 11)"
    THIRD_SECONDARY = "الثالث الثانوي (Grade 12)"
    UNIVERSITY = "الجامعة (University)"


class ActivityType(Enum):
    """أنواع الأنشطة اليومية"""
    STUDY = "دراسة"
    SLEEP = "نوم"
    FOOD = "طعام"
    EXERCISE = "رياضة"
    SOCIAL = "تواصل اجتماعي"
    ENTERTAINMENT = "ترفيه"
    PRAYER = "صلاة"
    REST = "استرخاء"
    WORK = "عمل"
    HOBBY = "هواية"


class MoodType(Enum):
    """حالات المزاج"""
    VERY_HAPPY = "سعيد جداً"
    HAPPY = "سعيد"
    NEUTRAL = "محايد"
    SAD = "حزين"
    VERY_SAD = "حزين جداً"


# ==================== الألوان والإعدادات ====================

class Colors:
    """تعريف الألوان المستخدمة في اللعبة"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (128, 0, 128)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    DARK_GREEN = (34, 139, 34)
    LIGHT_BLUE = (173, 216, 230)


class GameSettings:
    """إعدادات اللعبة"""
    WIDTH = 1400
    HEIGHT = 900
    FPS = 60
    CLOCK_SPEED = 5  # دقائق اللعبة لكل إطار

    # الحد الأدنى والأقصى للمتغيرات
    MIN_VALUE = 0
    MAX_ENERGY = 100
    MAX_MOOD = 100
    MAX_HEALTH = 100


# ==================== فئة الأنشطة ====================

class Activity:
    """تعريف النشاط اليومي"""

    def __init__(
        self,
        name: str,
        activity_type: ActivityType,
        duration_minutes: int,
        energy_cost: int,
        mood_change: int,
        health_change: int,
        description: str = ""
    ):
        self.name = name
        self.activity_type = activity_type
        self.duration_minutes = duration_minutes
        self.energy_cost = energy_cost
        self.mood_change = mood_change
        self.health_change = health_change
        self.description = description
        self.start_time = None
        self.is_completed = False
        self.completion_percentage = 0

    def start(self, current_time: datetime):
        """بدء النشاط"""
        self.start_time = current_time
        self.is_completed = False

    def update(self, elapsed_minutes: int):
        """تحديث تقدم النشاط"""
        if self.start_time is None:
            return

        self.completion_percentage = min(
            100,
            (elapsed_minutes / self.duration_minutes) * 100
        )

        if self.completion_percentage >= 100:
            self.is_completed = True

    def complete(self) -> Dict:
        """إكمال النشاط وإرجاع التأثيرات"""
        self.is_completed = True
        self.completion_percentage = 100
        return {
            "energy_cost": self.energy_cost,
            "mood_change": self.mood_change,
            "health_change": self.health_change
        }

    def __repr__(self):
        return f"Activity({self.name}, {self.duration_minutes}min)"


# ==================== فئة الموضوع الدراسي ====================

class Subject:
    """تعريف المادة الدراسية حسب الصف"""

    def __init__(
        self,
        name: str,
        grade: StudentGrade,
        difficulty: int,
        weekly_hours: int,
        importance: int = 5
    ):
        self.name = name
        self.grade = grade
        self.difficulty = difficulty  # من 1 إلى 10
        self.weekly_hours = weekly_hours
        self.importance = importance  # من 1 إلى 10
        self.study_hours = 0
        self.exam_score = 0
        self.progress = 0

    def study(self, minutes: int) -> int:
        """الدراسة وإرجاع النقاط المكتسبة"""
        study_hours = minutes / 60
        self.study_hours += study_hours

        # حساب التقدم
        points = int((study_hours / self.weekly_hours) * 100)
        self.progress = min(100, self.progress + points)

        return points

    def take_exam(self) -> int:
        """أخذ امتحان وحساب النتيجة"""
        base_score = 50
        if self.study_hours >= self.weekly_hours:
            base_score += 30
        elif self.study_hours >= self.weekly_hours * 0.5:
            base_score += 15
        elif self.study_hours >= self.weekly_hours * 0.25:
            base_score += 5

        # إضافة عشوائية
        self.exam_score = base_score + random.randint(-10, 20)
        self.exam_score = max(0, min(100, self.exam_score))

        return self.exam_score

    def get_recommendation(self) -> str:
        """الحصول على توصيات للدراسة"""
        if self.progress < 30:
            return f"⚠️ تحتاج إلى دراسة مكثفة في {self.name}"
        elif self.progress < 60:
            return f"📚 استمر في دراسة {self.name}"
        elif self.progress < 80:
            return f"👍 أداؤك جيد في {self.name}"
        else:
            return f"🌟 ممتاز! أنت متفوق في {self.name}"

    def __repr__(self):
        return f"Subject({self.name}, Progress: {self.progress}%)"


# ==================== فئة الطالب ====================

class Student:
    """تعريف الطالب والحالة الصحية والنفسية"""

    def __init__(self, name: str, grade: StudentGrade):
        self.name = name
        self.grade = grade
        self.age = self._get_age_from_grade(grade)

        # المتغيرات الأساسية
        self.energy = 100
        self.mood = 80
        self.health = 100
        self.stress_level = 20

        # الدراسة
        self.subjects: List[Subject] = []
        self.total_study_hours = 0
        self.gpa = 0

        # الإحصائيات
        self.total_activities_completed = 0
        self.streak_days = 0
        self.lifetime_mood = 0
        self.total_sleep_hours = 0

        # الأهداف
        self.goals = []
        self.achievements = []

        # الوقت
        self.current_game_time = datetime(2024, 1, 1, 6, 0, 0)
        self.last_update = self.current_game_time

        # إضافة المواد الافتراضية حسب الصف
        self._initialize_subjects()

    def _get_age_from_grade(self, grade: StudentGrade) -> int:
        """حساب العمر من الصف"""
        grades_map = {
            StudentGrade.FIRST_SECONDARY: 16,
            StudentGrade.SECOND_SECONDARY: 17,
            StudentGrade.THIRD_SECONDARY: 18,
            StudentGrade.UNIVERSITY: 20
        }
        return grades_map.get(grade, 16)

    def _initialize_subjects(self):
        """إضافة المواد الافتراضية حسب الصف"""
        subjects_map = {
            StudentGrade.FIRST_SECONDARY: [
                ("الرياضيات", 8, 5),
                ("العربية", 7, 4),
                ("الإنجليزية", 8, 4),
                ("العلوم", 7, 4),
                ("الجغرافيا", 5, 3),
                ("التاريخ", 5, 3),
            ],
            StudentGrade.SECOND_SECONDARY: [
                ("الرياضيات المتقدمة", 9, 6),
                ("الفيزياء", 8, 5),
                ("الكيمياء", 8, 5),
                ("الأحياء", 7, 4),
                ("العربية", 6, 4),
                ("الإنجليزية", 7, 4),
            ],
            StudentGrade.THIRD_SECONDARY: [
                ("الرياضيات التخصصية", 10, 7),
                ("الفيزياء المتقدمة", 9, 6),
                ("الكيمياء المتقدمة", 9, 6),
                ("الأحياء المتقدمة", 8, 5),
                ("العربية المتقدمة", 7, 4),
                ("الإنجليزية المتقدمة", 7, 4),
            ],
            StudentGrade.UNIVERSITY: [
                ("البرمجة", 8, 5),
                ("قواعد البيانات", 8, 5),
                ("الخوارزميات", 9, 6),
                ("الرياضيات المجردة", 9, 6),
                ("اللغات الطبيعية", 7, 4),
                ("النظم الموزعة", 8, 5),
            ]
        }

        subjects = subjects_map.get(self.grade, [])
        for name, difficulty, weekly_hours in subjects:
            self.subjects.append(
                Subject(name, self.grade, difficulty, weekly_hours)
            )

    def add_activity(self, activity: Activity):
        """إضافة نشاط"""
        activity.start(self.current_game_time)

    def study_subject(self, subject_index: int, minutes: int):
        """دراسة مادة معينة"""
        if 0 <= subject_index < len(self.subjects):
            subject = self.subjects[subject_index]
            points = subject.study(minutes)
            self.total_study_hours += minutes / 60
            self.energy = max(0, self.energy - int(minutes / 10))
            self.stress_level = max(0, self.stress_level - 5)
            return points
        return 0

    def do_activity(self, activity: Activity):
        """تنفيذ نشاط"""
        effects = activity.complete()

        self.energy = max(0, min(100, self.energy - effects["energy_cost"]))
        self.mood = max(0, min(100, self.mood + effects["mood_change"]))
        self.health = max(0, min(100, self.health + effects["health_change"]))

        self.total_activities_completed += 1
        self.lifetime_mood += self.mood

        return effects

    def get_mood_status(self) -> MoodType:
        """الحصول على حالة المزاج"""
        if self.mood >= 80:
            return MoodType.VERY_HAPPY
        elif self.mood >= 60:
            return MoodType.HAPPY
        elif self.mood >= 40:
            return MoodType.NEUTRAL
        elif self.mood >= 20:
            return MoodType.SAD
        else:
            return MoodType.VERY_SAD

    def get_health_status(self) -> str:
        """الحصول على حالة الصحة"""
        if self.health >= 80:
            return "ممتاز 💪"
        elif self.health >= 60:
            return "جيد ✅"
        elif self.health >= 40:
            return "متوسط ⚠️"
        else:
            return "سيء ❌"

    def update_gpa(self):
        """تحديث المعدل"""
        if self.subjects:
            total_score = sum(s.exam_score for s in self.subjects)
            self.gpa = total_score / len(self.subjects)

    def get_recommendation_message(self) -> str:
        """الحصول على رسالة توصية"""
        messages = []

        if self.energy < 30:
            messages.append("🔋 أنت متعب جداً، احصل على قسط من الراحة!")
        if self.mood < 30:
            messages.append("😢 حالتك النفسية متدهورة، قم بنشاط ممتع!")
        if self.health < 30:
            messages.append("🏥 صحتك في خطر، مارس الرياضة وتناول طعاماً صحياً!")
        if self.stress_level > 80:
            messages.append("😰 مستوى الإجهاد عالي جداً، استرخِ قليلاً!")

        if not messages:
            messages.append("✨ حالتك جيدة، استمر هكذا!")

        return " | ".join(messages)

    def __repr__(self):
        return (f"Student({self.name}, {self.grade.value}, "
                f"Energy: {self.energy}, Mood: {self.mood}, Health: {self.health})")


# ==================== فئة مخطط اليوم ====================

class DayPlanner:
    """تخطيط اليوم والأنشطة"""

    def __init__(self, student: Student):
        self.student = student
        self.activities: List[Activity] = []
        self.current_activity_index = 0
        self.day_activities_completed = 0
        self.daily_schedule: Dict[str, List[Activity]] = {}

        # الأنشطة المعرفة مسبقاً
        self._initialize_default_activities()

    def _initialize_default_activities(self):
        """تهيئة الأنشطة الافتراضية"""
        default_activities = [
            Activity("استيقاظ صباحي", ActivityType.REST, 30, 5, 10, 5,
                    "الاستيقاظ والتحضير الصباحي"),
            Activity("وضوء وصلاة الفجر", ActivityType.PRAYER, 20, 0, 15, 5,
                    "الوضوء والصلاة"),
            Activity("إفطار صحي", ActivityType.FOOD, 30, -20, 10, 15,
                    "تناول إفطار متوازن"),
            Activity("الذهاب للمدرسة", ActivityType.EXERCISE, 30, 10, 5, 5,
                    "تحرك جسدي"),
            Activity("الدراسة في المدرسة", ActivityType.STUDY, 360, 30, -5, 5,
                    "حضور الدروس"),
            Activity("صلاة الظهر", ActivityType.PRAYER, 15, 0, 10, 3,
                    "صلاة الظهر"),
            Activity("غداء صحي", ActivityType.FOOD, 30, -20, 15, 15,
                    "تناول غداء متوازن"),
            Activity("الراحة والاسترخاء", ActivityType.REST, 60, -30, 20, 10,
                    "الراحة النفسية"),
            Activity("دراسة منزلية", ActivityType.STUDY, 120, 15, -10, 5,
                    "دراسة المواد المدرسية"),
            Activity("هواية أو رياضة", ActivityType.HOBBY, 60, 10, 30, 20,
                    "نشاط ممتع ومريح"),
            Activity("تواصل اجتماعي", ActivityType.SOCIAL, 60, 0, 25, 5,
                    "التحدث مع الأصدقاء"),
            Activity("عشاء صحي", ActivityType.FOOD, 30, -20, 10, 15,
                    "تناول عشاء متوازن"),
            Activity("صلاة العشاء", ActivityType.PRAYER, 15, 0, 10, 3,
                    "صلاة العشاء"),
            Activity("ترفيه وتسلية", ActivityType.ENTERTAINMENT, 60, 5, 30, 5,
                    "الاستمتاع بأنشطة ممتعة"),
            Activity("نوم عميق", ActivityType.SLEEP, 480, -50, 10, 30,
                    "نوم صحي كافي"),
        ]

        self.activities = default_activities

    def add_custom_activity(self, activity: Activity):
        """إضافة نشاط مخصص"""
        self.activities.append(activity)

    def get_daily_activities(self) -> List[Activity]:
        """الحصول على أنشطة اليوم"""
        return self.activities

    def complete_current_activity(self) -> bool:
        """إكمال النشاط الحالي"""
        if self.current_activity_index < len(self.activities):
            activity = self.activities[self.current_activity_index]
            self.student.do_activity(activity)
            self.current_activity_index += 1
            self.day_activities_completed += 1
            return True
        return False

    def get_activity_details(self, index: int) -> Dict:
        """الحصول على تفاصيل النشاط"""
        if 0 <= index < len(self.activities):
            activity = self.activities[index]
            return {
                "name": activity.name,
                "type": activity.activity_type.value,
                "duration": activity.duration_minutes,
                "energy_cost": activity.energy_cost,
                "mood_change": activity.mood_change,
                "health_change": activity.health_change,
                "description": activity.description,
                "completed": activity.is_completed
            }
        return {}

    def calculate_daily_score(self) -> int:
        """حساب درجة اليوم"""
        score = 0

        # النشاطات المكتملة
        score += self.day_activities_completed * 10

        # حالة الطالب
        score += int(self.student.mood / 10)
        score += int(self.student.health / 10)
        score -= int(self.student.stress_level / 10)

        # الدراسة
        score += int(self.student.total_study_hours * 5)

        return max(0, score)


# ==================== فئة اللعبة الرئيسية ====================

class StudentLifeGame:
    """اللعبة الرئيسية"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (GameSettings.WIDTH, GameSettings.HEIGHT)
        )
        pygame.display.set_caption("🎓 لعبة تنظيم حياة الطالب الأردني")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)

        # حالة اللعبة
        self.game_state = "menu"  # menu, setup, playing, stats, game_over
        self.student = None
        self.day_planner = None
        self.selected_grade = None
        self.student_name = ""
        self.game_speed = 1
        self.paused = False
        self.day_count = 0
        self.game_time_elapsed = 0

        # العناصر التفاعلية
        self.buttons = {}
        self.text_input_active = False
        self.text_input_value = ""

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple,
        x: int,
        y: int,
        center: bool = False
    ) -> pygame.Rect:
        """رسم نص على الشاشة"""
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()

        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_button(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple,
        text_color: Tuple,
        button_id: str = None
    ) -> pygame.Rect:
        """رسم زر"""
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, button_rect, 2)

        text_rect = self.draw_text(text, self.font_small, text_color, x + width // 2, y + height // 2, center=True)

        if button_id:
            self.buttons[button_id] = button_rect

        return button_rect

    def draw_progress_bar(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        current: int,
        maximum: int,
        color: Tuple,
        text: str = ""
    ):
        """رسم شريط تقدم"""
        # الخلفية
        pygame.draw.rect(self.screen, Colors.LIGHT_GRAY, (x, y, width, height))
        pygame.draw.rect(self.screen, Colors.BLACK, (x, y, width, height), 2)

        # الملء
        if maximum > 0:
            fill_width = (current / maximum) * width
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # النص
        if text:
            self.draw_text(f"{text} {current}/{maximum}", self.font_tiny, Colors.BLACK, x + 10, y + 2)

    def handle_events(self):
        """معالجة الأحداث"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)

            if event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)

    def handle_mouse_click(self, pos: Tuple):
        """معالجة النقرات"""
        if self.game_state == "menu":
            self.handle_menu_click(pos)
        elif self.game_state == "setup":
            self.handle_setup_click(pos)
        elif self.game_state == "playing":
            self.handle_playing_click(pos)
        elif self.game_state == "stats":
            self.handle_stats_click(pos)

    def handle_key_press(self, key: int):
        """معالجة المفاتيح"""
        if key == pygame.K_ESCAPE:
            self.game_state = "menu"
        elif key == pygame.K_SPACE and self.game_state == "playing":
            self.paused = not self.paused
        elif self.text_input_active:
            if key == pygame.K_BACKSPACE:
                self.text_input_value = self.text_input_value[:-1]
            elif key == pygame.K_RETURN:
                self.text_input_active = False
            else:
                if len(self.text_input_value) < 30:
                    self.text_input_value += pygame.key.name(key)

    def handle_menu_click(self, pos: Tuple):
        """معالجة الضغط على القائمة الرئيسية"""
        if "start" in self.buttons and self.buttons["start"].collidepoint(pos):
            self.game_state = "setup"
        elif "quit" in self.buttons and self.buttons["quit"].collidepoint(pos):
            self.running = False

    def handle_setup_click(self, pos: Tuple):
        """معالجة الضغط على شاشة الإعداد"""
        # اختيار الصف
        grade_buttons = {
            "grade_10": StudentGrade.FIRST_SECONDARY,
            "grade_11": StudentGrade.SECOND_SECONDARY,
            "grade_12": StudentGrade.THIRD_SECONDARY,
            "grade_uni": StudentGrade.UNIVERSITY
        }

        for button_id, grade in grade_buttons.items():
            if button_id in self.buttons and self.buttons[button_id].collidepoint(pos):
                self.selected_grade = grade

        # زر ابدأ اللعبة
        if "start_game" in self.buttons and self.buttons["start_game"].collidepoint(pos):
            if self.selected_grade and self.student_name:
                self.create_student()
                self.game_state = "playing"

        # حقل الاسم
        if "name_input" in self.buttons and self.buttons["name_input"].collidepoint(pos):
            self.text_input_active = True

    def handle_playing_click(self, pos: Tuple):
        """معالجة الضغط أثناء اللعب"""
        if "do_activity" in self.buttons and self.buttons["do_activity"].collidepoint(pos):
            self.day_planner.complete_current_activity()

        if "stats" in self.buttons and self.buttons["stats"].collidepoint(pos):
            self.game_state = "stats"

        if "study" in self.buttons and self.buttons["study"].collidepoint(pos):
            self.student.study_subject(0, 60)

        if "rest" in self.buttons and self.buttons["rest"].collidepoint(pos):
            activity = Activity("راحة سريعة", ActivityType.REST, 30, 20, 15, 10)
            self.student.do_activity(activity)

    def handle_stats_click(self, pos: Tuple):
        """معالجة الضغط على إحصائيات"""
        if "back" in self.buttons and self.buttons["back"].collidepoint(pos):
            self.game_state = "playing"

    def create_student(self):
        """إنشاء طالب جديد"""
        self.student = Student(self.student_name, self.selected_grade)
        self.day_planner = DayPlanner(self.student)

    def draw_menu(self):
        """رسم القائمة الرئيسية"""
        self.screen.fill(Colors.DARK_GRAY)

        # العنوان
        self.draw_text(
            "🎓 لعبة تنظيم حياة الطالب الأردني",
            self.font_large,
            Colors.CYAN,
            GameSettings.WIDTH // 2,
            100,
            center=True
        )

        # الوصف
        self.draw_text(
            "رتب حياتك الدراسية والشخصية بذكاء",
            self.font_medium,
            Colors.YELLOW,
            GameSettings.WIDTH // 2,
            200,
            center=True
        )

        # الأزرار
        self.draw_button(
            "ابدأ اللعبة 🚀",
            GameSettings.WIDTH // 2 - 150,
            400,
            300,
            80,
            Colors.BLUE,
            Colors.WHITE,
            "start"
        )

        self.draw_button(
            "خروج ❌",
            GameSettings.WIDTH // 2 - 150,
            550,
            300,
            80,
            Colors.RED,
            Colors.WHITE,
            "quit"
        )

        # معلومات إضافية
        info_text = [
            "نظم وقتك بين الدراسة والحياة الشخصية",
            "اعتن بصحتك النفسية والجسدية",
            "حقق أحلامك الدراسية",
            "قم بنسخة سفاح من هذه اللعبة للمملكة! 🇯🇴"
        ]

        for i, text in enumerate(info_text):
            self.draw_text(
                text,
                self.font_small,
                Colors.LIGHT_GRAY,
                GameSettings.WIDTH // 2,
                700 + i * 40,
                center=True
            )

    def draw_setup(self):
        """رسم شاشة الإعداد"""
        self.screen.fill(Colors.DARK_GRAY)

        # العنوان
        self.draw_text(
            "إنشاء ملف الطالب",
            self.font_large,
            Colors.CYAN,
            GameSettings.WIDTH // 2,
            50,
            center=True
        )

        # اختيار الصف
        self.draw_text(
            "اختر صفك:",
            self.font_medium,
            Colors.YELLOW,
            50,
            150
        )

        grades = [
            ("الأول الثانوي", "grade_10", StudentGrade.FIRST_SECONDARY),
            ("الثاني الثانوي", "grade_11", StudentGrade.SECOND_SECONDARY),
            ("الثالث الثانوي", "grade_12", StudentGrade.THIRD_SECONDARY),
            ("الجامعة", "grade_uni", StudentGrade.UNIVERSITY),
        ]

        x_start = 50
        for i, (label, btn_id, grade) in enumerate(grades):
            is_selected = self.selected_grade == grade
            color = Colors.GREEN if is_selected else Colors.BLUE

            self.draw_button(
                label,
                x_start + i * 300,
                250,
                250,
                60,
                color,
                Colors.WHITE,
                btn_id
            )

        # اسم الطالب
        self.draw_text(
            "اسمك:",
            self.font_medium,
            Colors.YELLOW,
            50,
            400
        )

        name_input_rect = pygame.Rect(50, 450, 400, 50)
        pygame.draw.rect(self.screen, Colors.WHITE, name_input_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, name_input_rect, 2)
        self.buttons["name_input"] = name_input_rect

        self.draw_text(
            self.text_input_value if self.text_input_active else "اكتب اسمك هنا",
            self.font_small,
            Colors.BLACK,
            60,
            465
        )

        # زر البدء
        is_ready = self.selected_grade and self.text_input_value
        button_color = Colors.GREEN if is_ready else Colors.GRAY

        self.draw_button(
            "ابدأ اللعبة",
            GameSettings.WIDTH // 2 - 150,
            600,
            300,
            80,
            button_color,
            Colors.WHITE,
            "start_game"
        )

        if is_ready:
            self.student_name = self.text_input_value

    def draw_playing(self):
        """رسم شاشة اللعب"""
        self.screen.fill(Colors.DARK_GRAY)

        # معلومات الطالب العلوية
        self.draw_text(
            f"👤 {self.student.name} | {self.student.grade.value}",
            self.font_medium,
            Colors.CYAN,
            20,
            10
        )

        self.draw_text(
            f"📅 اليوم #{self.day_count} | الوقت: {self.student.current_game_time.strftime('%H:%M')}",
            self.font_small,
            Colors.YELLOW,
            20,
            50
        )

        # الحالة الصحية والنفسية
        y_pos = 100
        self.draw_text("الحالة:", self.font_medium, Colors.YELLOW, 20, y_pos)

        # الطاقة
        y_pos += 50
        self.draw_text("⚡ الطاقة:", self.font_small, Colors.WHITE, 20, y_pos)
        self.draw_progress_bar(200, y_pos + 5, 300, 20, int(self.student.energy), 100, Colors.ORANGE)

        # المزاج
        y_pos += 50
        self.draw_text("😊 المزاج:", self.font_small, Colors.WHITE, 20, y_pos)
        self.draw_progress_bar(200, y_pos + 5, 300, 20, int(self.student.mood), 100, Colors.PINK)

        # الصحة
        y_pos += 50
        self.draw_text("❤️ الصحة:", self.font_small, Colors.WHITE, 20, y_pos)
        self.draw_progress_bar(200, y_pos + 5, 300, 20, int(self.student.health), 100, Colors.RED)

        # الإجهاد
        y_pos += 50
        self.draw_text("😰 الإجهاد:", self.font_small, Colors.WHITE, 20, y_pos)
        self.draw_progress_bar(200, y_pos + 5, 300, 20, int(self.student.stress_level), 100, Colors.RED)

        # الأنشطة الحالية
        y_pos = 100
        x_pos = 700
        self.draw_text("📋 الأنشطة اليومية:", self.font_medium, Colors.YELLOW, x_pos, y_pos)

        for i in range(min(5, len(self.day_planner.activities))):
            activity = self.day_planner.activities[i]
            y_pos += 50

            status = "✅" if activity.is_completed else "⏳"
            activity_text = f"{status} {activity.name} ({activity.duration_minutes}دقيقة)"

            color = Colors.GREEN if activity.is_completed else Colors.LIGHT_GRAY
            self.draw_text(activity_text, self.font_tiny, color, x_pos, y_pos)

        # الأزرار الفعّالة
        button_y = 650
        self.draw_button(
            "قم بنشاط الآن 🎬",
            50,
            button_y,
            200,
            60,
            Colors.GREEN,
            Colors.WHITE,
            "do_activity"
        )

        self.draw_button(
            "ادرس 📚",
            300,
            button_y,
            200,
            60,
            Colors.BLUE,
            Colors.WHITE,
            "study"
        )

        self.draw_button(
            "استرخِ 😴",
            550,
            button_y,
            200,
            60,
            Colors.PURPLE,
            Colors.WHITE,
            "rest"
        )

        self.draw_button(
            "الإحصائيات 📊",
            800,
            button_y,
            200,
            60,
            Colors.ORANGE,
            Colors.WHITE,
            "stats"
        )

        # التوصية
        recommendation = self.student.get_recommendation_message()
        self.draw_text(
            recommendation,
            self.font_small,
            Colors.YELLOW,
            GameSettings.WIDTH // 2,
            830,
            center=True
        )

    def draw_stats(self):
        """رسم شاشة الإحصائيات"""
        self.screen.fill(Colors.DARK_GRAY)

        # العنوان
        self.draw_text(
            f"📊 إحصائيات {self.student.name}",
            self.font_large,
            Colors.CYAN,
            GameSettings.WIDTH // 2,
            20,
            center=True
        )

        # المعلومات الأساسية
        y_pos = 100
        info_items = [
            (f"الصف: {self.student.grade.value}", "blue"),
            (f"العمر: {self.student.age} سنة", "blue"),
            (f"الأيام المعيشة: {self.day_count}", "yellow"),
            (f"النشاطات المكملة: {self.student.total_activities_completed}", "green"),
            (f"ساعات الدراسة: {self.student.total_study_hours:.1f} ساعة", "yellow"),
            (f"المعدل: {self.student.gpa:.2f}", "orange" if self.student.gpa >= 70 else "red"),
            (f"الحالة الصحية: {self.student.get_health_status()}", "white"),
            (f"حالة المزاج: {self.student.get_mood_status().value}", "white"),
        ]

        for text, color_key in info_items:
            color = getattr(Colors, color_key.upper(), Colors.WHITE)
            self.draw_text(text, self.font_medium, color, 50, y_pos)
            y_pos += 50

        # المواد الدراسية
        y_pos += 30
        self.draw_text("📚 المواد الدراسية:", self.font_medium, Colors.YELLOW, 50, y_pos)
        y_pos += 50

        for subject in self.student.subjects[:6]:
            subject_info = f"{subject.name}: {subject.progress}% | نتيجة: {subject.exam_score}/100"
            color = Colors.GREEN if subject.progress > 70 else Colors.YELLOW if subject.progress > 40 else Colors.RED
            self.draw_text(subject_info, self.font_small, color, 50, y_pos)
            y_pos += 40

        # الزر للعودة
        self.draw_button(
            "العودة للعبة ←",
            GameSettings.WIDTH // 2 - 150,
            800,
            300,
            80,
            Colors.BLUE,
            Colors.WHITE,
            "back"
        )

    def update(self):
        """تحديث حالة اللعبة"""
        if self.game_state == "playing" and not self.paused:
            # تحديث الوقت
            self.game_time_elapsed += GameSettings.CLOCK_SPEED
            self.student.current_game_time += timedelta(minutes=GameSettings.CLOCK_SPEED)

            # تحديث يومي
            if self.game_time_elapsed >= 1440:  # 24 ساعة
                self.game_time_elapsed = 0
                self.day_count += 1
                self.day_planner.day_activities_completed = 0
                self.student.update_gpa()

            # تحديث الحالة تلقائياً
            self.update_student_status()

    def update_student_status(self):
        """تحديث حالة الطالب تلقائياً"""
        # فقدان الطاقة بسبب الوقت
        self.student.energy = max(0, self.student.energy - 0.1)

        # تحسن الصحة النفسية مع الراحة
        if self.student.mood < 100:
            self.student.mood = min(100, self.student.mood + 0.05)

        # تأثير الإجهاد على الصحة
        self.student.health = max(0, self.student.health - (self.student.stress_level / 1000))

        # زيادة الإجهاد مع عدم الدراسة
        if self.day_planner.day_activities_completed < 5:
            self.student.stress_level = min(100, self.student.stress_level + 0.1)
        else:
            self.student.stress_level = max(0, self.student.stress_level - 0.1)

    def draw(self):
        """رسم اللعبة"""
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "setup":
            self.draw_setup()
        elif self.game_state == "playing":
            self.draw_playing()
        elif self.game_state == "stats":
            self.draw_stats()

        # مؤشر توقف اللعبة
        if self.paused:
            self.draw_text(
                "⏸ اللعبة موقوفة",
                self.font_large,
                Colors.RED,
                GameSettings.WIDTH // 2,
                GameSettings.HEIGHT // 2,
                center=True
            )

        pygame.display.flip()

    def run(self):
        """تشغيل اللعبة الرئيسي"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(GameSettings.FPS)

        pygame.quit()
        sys.exit()


# ==================== نقطة البداية ====================

if __name__ == "__main__":
    game = StudentLifeGame()
    game.run()
