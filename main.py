#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日论文更新 — Android 版（Kivy）
================================
在手机上检索 PubMed 最新论文，按 13 个研究方向分类浏览，点击 DOI 跳转原文。
纯 Python 标准库 + Kivy，可用 buildozer 打包为 APK。
"""
import json, re, threading, time
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import Counter

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.core.text import LabelBase

# 注册中文字体（Noto Sans SC，开源 OFL 许可），覆盖 Kivy 默认字体以支持中文显示
LabelBase.register(name="Roboto", fn_regular="NotoSansSC.ttf")

# ===================== 13 个研究方向 =====================
TOPICS = [
    ("天然产物", ["natural products", "natural compounds", "phytochemistry"]),
    ("纳米递送", ["nanodelivery", "nanocarrier", "nanoparticle drug delivery"]),
    ("中药", ["traditional Chinese medicine", "Chinese herbal medicine"]),
    ("中医", ["TCM", "acupuncture", "meridian", "moxibustion"]),
    ("食品科学", ["food science", "functional food", "nutraceutical"]),
    ("低GI", ["low glycemic index", "glycemic control"]),
    ("心血管疾病", ["cardiovascular disease treatment", "cardioprotective"]),
    ("糖尿病", ["diabetes treatment", "antidiabetic", "insulin resistance"]),
    ("高尿酸/痛风", ["hyperuricemia", "gout treatment", "xanthine oxidase inhibitor"]),
    ("抑菌", ["antibacterial", "antimicrobial", "antibacterial activity"]),
    ("抗耐药菌", ["antimicrobial resistance", "MRSA", "multidrug-resistant"]),
    ("抗炎", ["anti-inflammatory", "inflammation"]),
    ("美白祛斑", ["skin whitening", "anti-melanogenic", "tyrosinase inhibition"]),
]
TOPIC_COLORS = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899",
                "#06b6d4", "#84cc16", "#f97316", "#6366f1", "#14b8a6", "#e11d48", "#a855f7"]

UA = {"User-Agent": "DailyPaperUpdate-Android/1.0"}


def open_url(url):
    """打开外部链接（Android 上 webbrowser 会转为系统 Intent）。"""
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


def fetch_pubmed(topic_name, keywords, days, max_results=15):
    """使用 PubMed E-utilities 检索论文（含摘要），纯标准库。"""
    papers = []
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    kw_parts = [f'"{k}"' if " " in k else k for k in keywords[:4]]
    kw_str = " OR ".join(kw_parts)
    ds = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
    de = datetime.now().strftime("%Y/%m/%d")
    query = f'({kw_str}) AND ("{ds}"[Date - Publication] : "{de}"[Date - Publication])'

    try:
        # 1) ESearch
        url = f"{base}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}" \
              f"&retmax={max_results}&sort=pubdate&retmode=json"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as resp:
            id_list = json.loads(resp.read()).get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return papers

        # 2) ESummary
        url2 = f"{base}/esummary.fcgi?db=pubmed&id={','.join(id_list)}&retmode=json"
        req2 = urllib.request.Request(url2, headers=UA)
        with urllib.request.urlopen(req2, timeout=30) as resp2:
            results = json.loads(resp2.read()).get("result", {})

        # 3) EFetch 摘要
        abstracts = {}
        try:
            url3 = f"{base}/efetch.fcgi?db=pubmed&id={','.join(id_list)}" \
                   f"&rettype=abstract&retmode=xml"
            req3 = urllib.request.Request(url3, headers=UA)
            with urllib.request.urlopen(req3, timeout=60) as resp3:
                root = ET.fromstring(resp3.read().decode("utf-8", errors="replace"))
            for article in root.iter("PubmedArticle"):
                pmid_el = article.find(".//PMID")
                if pmid_el is None or not pmid_el.text:
                    continue
                parts = [abt.text for abt in article.findall(".//AbstractText") if abt.text]
                if parts:
                    abstracts[pmid_el.text] = " ".join(parts)
        except Exception:
            pass

        for pmid in id_list:
            if pmid not in results or pmid == "uids":
                continue
            art = results[pmid]
            doi = ""
            for aid in art.get("articleids", []):
                if aid.get("idtype") == "doi":
                    doi = aid["value"]
                    break
            authors_list = [a.get("name", "") for a in art.get("authors", [])]
            authors = ", ".join(authors_list[:6])
            if len(authors_list) > 6:
                authors += " et al."
            papers.append({
                "pmid": pmid, "doi": doi,
                "title": art.get("title", ""),
                "authors": authors,
                "journal": art.get("source", ""),
                "pubdate": art.get("pubdate", ""),
                "abstract": abstracts.get(pmid, ""),
                "topic_cn": topic_name,
            })
    except Exception:
        pass
    return papers


def make_summary(p, limit=160):
    clean = re.sub(r'<[^>]+>', '', p.get("abstract", "") or "").strip()
    if len(clean) < 30:
        return p.get("title", "")
    return clean[:limit] + ("..." if len(clean) > limit else "")


# ===================== UI：主题选择行 =====================
class TopicRow(BoxLayout):
    def __init__(self, name, **kw):
        super().__init__(**kw)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = [dp(6), 0]
        self.spacing = dp(4)
        self.cb = CheckBox(size_hint=(None, None), size=(dp(40), dp(40)))
        lbl = Label(text=name, halign="left", valign="middle", font_size=15)
        lbl.bind(size=lambda s, sz: setattr(s, "text_size", (sz[0], None)))
        self.add_widget(self.cb)
        self.add_widget(lbl)


# ===================== 结果卡片 =====================
class PaperCard(BoxLayout):
    def __init__(self, paper, **kw):
        super().__init__(**kw)
        self.paper = paper
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(196)
        self.padding = dp(10)
        self.spacing = dp(4)

        title = Label(text=paper.get("title", ""), font_size=15, bold=True,
                      halign="left", valign="top", size_hint_y=None, height=dp(44),
                      shorten=True, shorten_from="right", max_lines=2)
        title.bind(size=lambda s, sz: setattr(s, "text_size", (sz[0], None)))
        title.bind(texture_size=lambda s, sz: setattr(s, "height", min(dp(44), sz[1] + dp(4))))

        meta = Label(text=f"{paper.get('authors', '')}\n{paper.get('journal', '')} · {paper.get('pubdate', '')}",
                     font_size=12, color=(0.45, 0.48, 0.52, 1), halign="left", valign="top",
                     size_hint_y=None, height=dp(36), shorten=True, shorten_from="right", max_lines=2)
        meta.bind(size=lambda s, sz: setattr(s, "text_size", (sz[0], None)))

        ab = Label(text=make_summary(paper), font_size=13, color=(0.2, 0.22, 0.25, 1),
                   halign="left", valign="top", size_hint_y=None, height=dp(64),
                   shorten=True, shorten_from="right", max_lines=3)
        ab.bind(size=lambda s, sz: setattr(s, "text_size", (sz[0], None)))

        bottom = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34), spacing=dp(8))
        tag = Label(text=f"  {paper.get('topic_cn', '')}  ", font_size=12, bold=True,
                    size_hint_x=None, width=dp(90), halign="center", valign="middle")
        tag.bind(size=lambda s, sz: setattr(s, "text_size", (sz[0], None)))
        btn = Button(text="📄 查看原文 DOI", font_size=13, size_hint_x=1)
        if paper.get("doi"):
            btn.bind(on_release=lambda *a: open_url(f"https://doi.org/{paper['doi']}"))
        else:
            btn.disabled = True
            btn.text = "无 DOI"
        bottom.add_widget(tag)
        bottom.add_widget(btn)

        self.add_widget(title)
        self.add_widget(meta)
        self.add_widget(ab)
        self.add_widget(bottom)


# ===================== 屏幕 1：设置 =====================
class SetupScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        root.add_widget(Label(text="📚 每日论文更新", font_size=22, bold=True,
                              size_hint_y=None, height=dp(40)))
        root.add_widget(Label(text="勾选研究方向，点击「开始更新」检索 PubMed 最新论文",
                              font_size=13, color=(0.45, 0.48, 0.52, 1),
                              size_hint_y=None, height=dp(24)))

        # 主题列表
        self.grid = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        for name, _ in TOPICS:
            row = TopicRow(name)
            self.rows.append(row)
            self.grid.add_widget(row)
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        root.add_widget(scroll)

        # 全选 / 全不选
        selrow = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))
        selrow.add_widget(Button(text="全选", on_release=lambda *a: self.set_all(True)))
        selrow.add_widget(Button(text="全不选", on_release=lambda *a: self.set_all(False)))
        root.add_widget(selrow)

        # 天数
        drow = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))
        drow.add_widget(Label(text="检索天数：", size_hint_x=None, width=dp(90)))
        self.days_input = TextInput(text="3", input_filter="int", multiline=False,
                                    size_hint_x=None, width=dp(80), font_size=16)
        drow.add_widget(self.days_input)
        drow.add_widget(Label(text="天", size_hint_x=None, width=dp(30)))
        drow.add_widget(Label())
        root.add_widget(drow)

        # 进度
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(8))
        root.add_widget(self.progress)
        self.status = Label(text="就绪", font_size=13, size_hint_y=None, height=dp(24))
        root.add_widget(self.status)

        # 开始按钮
        self.go = Button(text="🚀 开始更新", font_size=18, bold=True,
                         size_hint_y=None, height=dp(54))
        self.go.bind(on_release=self.start_update)
        root.add_widget(self.go)

        self.add_widget(root)

    def set_all(self, val):
        for r in self.rows:
            r.cb.active = val

    def start_update(self, *a):
        selected = [TOPICS[i] for i, r in enumerate(self.rows) if r.cb.active]
        if not selected:
            self._popup("请至少勾选一个研究方向")
            return
        days = int(self.days_input.text or "3") if (self.days_input.text or "").isdigit() else 3
        days = max(1, min(30, days))
        self.go.disabled = True
        self.progress.max = len(selected)
        self.progress.value = 0
        self.status.text = f"开始检索 {len(selected)} 个方向..."
        threading.Thread(target=self._run, args=(selected, days), daemon=True).start()

    def _run(self, selected, days):
        all_papers, seen_doi, seen_title = [], set(), set()
        for idx, (name, kws) in enumerate(selected):
            Clock.schedule_once(lambda dt, i=idx, n=name: self._tick(i, n), 0)
            ps = fetch_pubmed(name, kws, days)
            for p in ps:
                doi = p.get("doi", "").lower().strip()
                tk = (p.get("title", "") or "").lower().strip()[:80]
                if (doi and doi in seen_doi) or (tk and tk in seen_title):
                    continue
                if doi:
                    seen_doi.add(doi)
                if tk:
                    seen_title.add(tk)
                all_papers.append(p)
            time.sleep(0.3)
        all_papers.sort(key=lambda p: p.get("pubdate", ""), reverse=True)
        Clock.schedule_once(lambda dt: self._finish(all_papers), 0)

    def _tick(self, idx, name):
        self.progress.value = idx + 1
        self.status.text = f"[{idx + 1}/{self.progress.max}] 检索 {name}..."

    def _finish(self, papers):
        self.go.disabled = False
        self.progress.value = self.progress.max
        self.status.text = f"✅ 完成，共 {len(papers)} 篇论文"
        app = App.get_running_app()
        app.results_screen.show(papers)
        app.sm.current = "results"

    def _popup(self, msg):
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        box.add_widget(Label(text=msg))
        btn = Button(text="确定", size_hint_y=None, height=dp(44))
        box.add_widget(btn)
        p = Popup(title="提示", content=box, size_hint=(0.8, 0.4))
        btn.bind(on_release=p.dismiss)
        p.open()


# ===================== 屏幕 2：结果 =====================
class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        back = Button(text="← 返回", size_hint_x=None, width=dp(100),
                      on_release=lambda *a: setattr(App.get_running_app().sm, "current", "setup"))
        self.count_lbl = Label(text="", font_size=16, bold=True)
        header.add_widget(back)
        header.add_widget(self.count_lbl)
        root.add_widget(header)

        self.list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.list.bind(minimum_height=self.list.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        self.add_widget(root)

    def show(self, papers):
        self.list.clear_widgets()
        grouped = {}
        for p in papers:
            grouped.setdefault(p.get("topic_cn", "其他"), []).append(p)
        dist = " · ".join(f"{k} {len(v)}" for k, v in grouped.items())
        self.count_lbl.text = f"共 {len(papers)} 篇"
        for p in papers:
            self.list.add_widget(PaperCard(p))
        if not papers:
            self.list.add_widget(Label(text="未检索到论文，请扩大检索天数后重试",
                                       size_hint_y=None, height=dp(48)))


# ===================== App =====================
class PaperApp(App):
    title = "每日论文更新"

    def build(self):
        self.sm = ScreenManager()
        self.setup_screen = SetupScreen(name="setup")
        self.results_screen = ResultsScreen(name="results")
        self.sm.add_widget(self.setup_screen)
        self.sm.add_widget(self.results_screen)
        Window.bind(on_keyboard=self._on_keyboard)
        return self.sm

    def _on_keyboard(self, window, key, *args):
        # Android 返回键
        if key == 27:
            if self.sm.current == "results":
                self.sm.current = "setup"
                return True
        return False


if __name__ == "__main__":
    PaperApp().run()
