const pptxgen = require("pptxgenjs");

// ─── Nordic Modern Color Palette ───
const C = {
  darkBg:    "1E2D3D",  // deep navy slate (title/conclusion)
  darkBg2:   "2C3E50",  // slightly lighter navy
  lightBg:   "F5F7FA",  // very light gray-blue
  cardBg:    "FFFFFF",  // white cards
  accent:    "5B8A9C",  // muted teal-blue (Nordic)
  accentGold:"D4A76A",  // warm gold accent
  accentLight:"E3EEF2", // very light teal
  textDark:  "2C3E50",  // dark text
  textMid:   "5A6B7D",  // medium gray
  textLight: "FFFFFF",  // white text
  border:    "E0E6ED",  // subtle border
  divider:   "D4DCE4",  // divider line
  barColor:  "4A7B8D",  // accent bar color
  tagBg:     "EDF2F5",  // tag background
};

// ─── Helper: fresh shadow (never reuse objects!) ───
const cardShadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 });
const thinShadow = () => ({ type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.06 });

// ─── Helper: left accent bar ───
function addLeftBar(slide, pres, y, h, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: y, w: 0.08, h: h,
    fill: { color: color || C.accent }
  });
}

// ─── Helper: page number ───
function addPageNum(slide, num, total) {
  slide.addText(`${num} / ${total}`, {
    x: 8.8, y: 5.25, w: 1, h: 0.3,
    fontSize: 8, fontFace: "Calibri", color: C.textMid,
    align: "right"
  });
}

// ─── Helper: slide subtitle line at top ───
function addSlideHeader(slide, pres, title, subtitle) {
  // Top accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.04,
    fill: { color: C.accent }
  });
  // Title
  slide.addText(title, {
    x: 0.7, y: 0.3, w: 8.6, h: 0.55,
    fontSize: 26, fontFace: "Georgia", color: C.textDark, bold: true,
    margin: 0
  });
  // Subtitle line
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.7, y: 0.85, w: 8.6, h: 0.35,
      fontSize: 12, fontFace: "Calibri", color: C.textMid, italic: true,
      margin: 0
    });
  }
  // Thin divider
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 1.2, w: 2.0, h: 0.02,
    fill: { color: C.divider }
  });
}

// ─── Helper: card with left accent ───
function addCard(slide, pres, x, y, w, h, accentColor) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: w, h: h,
    fill: { color: C.cardBg },
    shadow: cardShadow()
  });
  // Left accent line on card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 0.06, h: h,
    fill: { color: accentColor || C.accent }
  });
}

// ─── Helper: speaker note (Korean - ~1 minute) ───
function setNotes(slide, text) {
  slide.addNotes(text);
}

// ═══════════════════════════════════════════════════════════════
//  MAIN
// ═══════════════════════════════════════════════════════════════

async function createPresentation() {
  let pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
  pres.author = "ABC-RAG Project";
  pres.title = "신규 도서 기획 제안서 - YES24 IT 모바일 베스트셀러 데이터 기반";

  const TOTAL = 15;

  // ═══════════════════════════════════════════════════════════
  // SLIDE 1 — Title (dark bg)
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.darkBg };

    // Large decorative circle (subtle)
    slide.addShape(pres.shapes.OVAL, {
      x: 6.5, y: -1.5, w: 5, h: 5,
      fill: { color: C.darkBg2, transparency: 60 }
    });
    slide.addShape(pres.shapes.OVAL, {
      x: 7.5, y: 3, w: 3.5, h: 3.5,
      fill: { color: C.darkBg2, transparency: 70 }
    });

    // Accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.8, y: 1.0, w: 0.08, h: 2.0,
      fill: { color: C.accentGold }
    });

    // Main title
    slide.addText("신규 도서 기획 제안서", {
      x: 1.2, y: 1.1, w: 7, h: 0.9,
      fontSize: 38, fontFace: "Georgia", color: C.textLight, bold: true,
      margin: 0
    });

    // Subtitle
    slide.addText("YES24 IT 모바일 베스트셀러 데이터 기반\n시장 분석 및 출간 전략", {
      x: 1.2, y: 2.1, w: 6, h: 0.7,
      fontSize: 16, fontFace: "Calibri", color: C.accentGold,
      margin: 0
    });

    // Bottom info
    slide.addText("2026. 07. 17  |  ABC-RAG 프로젝트", {
      x: 1.2, y: 4.6, w: 5, h: 0.4,
      fontSize: 11, fontFace: "Calibri", color: C.textMid,
      margin: 0
    });

    setNotes(slide,
      "안녕하십니까. 오늘 YES24 IT 모바일 베스트셀러 데이터를 기반으로 한 신규 도서 기획 제안서를 발표드리겠습니다. " +
      "AI 기술의 급속한 발전과 함께 IT 도서 시장은 새로운 전환점을 맞이하고 있습니다. " +
      "본 제안에서는 최신 시장 데이터 분석을 통해 가장 경쟁력 있는 신규 도서 주제와 출간 전략을 제시하고자 합니다. " +
      "약 15분 정도 소요될 예정입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 2 — Agenda
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "Agenda", "발표 순서");

    const items = [
      { num: "01", title: "시장 현황 분석", desc: "YES24 IT 모바일 베스트셀러 시장 개요" },
      { num: "02", title: "트렌드 인사이트", desc: "주요 카테고리 및 키워드 트렌드" },
      { num: "03", title: "경쟁 구도 분석", desc: "출판사별 포지셔닝 및 TOP 10 분석" },
      { num: "04", title: "독자 니즈 분석", desc: "가격·평점·리뷰 데이터 기반 인사이트" },
      { num: "05", title: "신규 도서 제안", desc: "주제 선정 및 콘텐츠 전략" },
      { num: "06", title: "출간 및 마케팅 전략", desc: "일정, 채널, 예상 손익" },
    ];

    items.forEach((item, i) => {
      const yBase = 1.5 + i * 0.62;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 8.6, h: 0.5,
        fill: { color: C.cardBg },
        shadow: thinShadow()
      });
      slide.addText(item.num, {
        x: 0.85, y: yBase, w: 0.5, h: 0.5,
        fontSize: 16, fontFace: "Georgia", color: C.accent, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(item.title, {
        x: 1.4, y: yBase, w: 2.5, h: 0.5,
        fontSize: 13, fontFace: "Calibri", color: C.textDark, bold: true,
        valign: "middle", margin: 0
      });
      slide.addText(item.desc, {
        x: 3.9, y: yBase, w: 5.2, h: 0.5,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        valign: "middle", margin: 0
      });
    });

    addPageNum(slide, 2, TOTAL);
    setNotes(slide,
      "발표 순서입니다. 먼저 YES24 IT 모바일 베스트셀러 데이터를 기반으로 한 시장 현황을 분석하고, " +
      "주요 트렌드와 경쟁 구도를 살펴보겠습니다. 이후 독자 니즈 분석을 통해 인사이트를 도출하고, " +
      "이를 바탕으로 한 신규 도서 제안과 출간 전략을 발표드리겠습니다. " +
      "마지막으로 예상 일정과 손익 구조까지 말씀드리겠습니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 3 — Market Overview (large stats)
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "시장 현황 분석", "YES24 IT 모바일 베스트셀러 데이터 개요");

    // Key stats row
    const stats = [
      { num: "25", label: "TOP 25위까지\n베스트셀러 분석", color: C.accent },
      { num: "16", label: "AI 직결 도서\n64% 점유", color: C.darkBg },
      { num: "10.0", label: "평균 평점\n(10점 만점)", color: C.accentGold },
    ];

    stats.forEach((s, i) => {
      const xBase = 0.7 + i * 3.05;
      addCard(slide, pres, xBase, 1.5, 2.8, 1.5, s.color);
      slide.addText(s.num, {
        x: xBase + 0.2, y: 1.6, w: 2.4, h: 0.7,
        fontSize: 36, fontFace: "Georgia", color: s.color, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(s.label, {
        x: xBase + 0.15, y: 2.35, w: 2.5, h: 0.5,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        align: "center", valign: "middle", margin: 0
      });
    });

    // Market description
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 3.3, w: 8.6, h: 1.8,
      fill: { color: C.cardBg },
      shadow: cardShadow()
    });
    addLeftBar(slide, pres, 3.3, 1.8, C.accent);

    slide.addText([
      { text: "시장 특징", options: { bold: true, fontSize: 14, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• AI 기술 도서가 전체 베스트셀러의 64% 이상을 차지하며 시장을 주도", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• 클로드(Claude), 챗GPT, 제미나이 등 생성형 AI 플랫폼별 실전 활용서가 강세", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• '바이브 코딩(Vibe Coding)', '에이전틱 코딩' 등 새로운 패러다임 서적 급부상", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• 교사 대상 AI 에듀테크 도서가 25% 차지 — 교육 분야로 AI 열풍 확산", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark } },
    ], {
      x: 1.0, y: 3.45, w: 8.0, h: 1.5,
      valign: "top", margin: 0
    });

    addPageNum(slide, 3, TOTAL);
    setNotes(slide,
      "시장 현황 분석 결과입니다. YES24 IT 모바일 베스트셀러 TOP 25위 데이터를 분석한 결과, " +
      "AI 관련 도서가 무려 64%를 차지하며 시장을 완전히 주도하고 있습니다. " +
      "특히 클로드, 챗GPT, 제미나이 등 생성형 AI 플랫폼별 실전 활용서가 강세를 보이고 있고, " +
      "바이브 코딩이나 에이전틱 코딩과 같은 새로운 개발 패러다임 서적도 급부상 중입니다. " +
      "주목할 점은 교사 대상 AI 에듀테크 도서가 25%를 차지하며 교육 분야로 AI 열풍이 확산되고 있다는 것입니다. " +
      "평균 평점은 10점 만점에 9.8점으로 매우 높아, 독자들의 만족도가 높은 시장입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 4 — Trend Insights
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "트렌드 인사이트", "3대 메가 트렌드");

    const trends = [
      {
        tag: "TREND 01",
        title: "생성형 AI 실전 활용",
        desc: "ChatGPT · Claude · Gemini 각 플랫폼의\n특화된 실무 활용법을 다루는 도서가\n베스트셀러 상위권을 차지",
        color: C.accent
      },
      {
        tag: "TREND 02",
        title: "AI 기반 개발 패러다임",
        desc: "Vibe Coding · Agentic Coding ·\nHarness Engineering 등 AI와 함께\n개발하는 새로운 방법론 부상",
        color: C.darkBg
      },
      {
        tag: "TREND 03",
        title: "교육 분야 AI 확산",
        desc: "2022 개정 교육과정과 맞물려\n교사 대상 AI 에듀테크 활용서가\n꾸준한 수요를 형성",
        color: C.accentGold
      },
    ];

    trends.forEach((t, i) => {
      const xBase = 0.7 + i * 3.05;
      addCard(slide, pres, xBase, 1.5, 2.8, 3.5, t.color);

      // Tag
      slide.addShape(pres.shapes.RECTANGLE, {
        x: xBase + 0.2, y: 1.7, w: 1.1, h: 0.3,
        fill: { color: t.color }
      });
      slide.addText(t.tag, {
        x: xBase + 0.2, y: 1.7, w: 1.1, h: 0.3,
        fontSize: 8, fontFace: "Calibri", color: C.textLight, bold: true,
        align: "center", valign: "middle", margin: 0
      });

      // Title
      slide.addText(t.title, {
        x: xBase + 0.2, y: 2.15, w: 2.4, h: 0.5,
        fontSize: 15, fontFace: "Georgia", color: C.textDark, bold: true,
        margin: 0
      });

      // Description
      slide.addText(t.desc, {
        x: xBase + 0.2, y: 2.8, w: 2.4, h: 1.6,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        margin: 0
      });
    });

    // Bottom insight
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 5.0, w: 8.6, h: 0.01,
      fill: { color: C.divider }
    });
    slide.addText("\"단순한 AI 사용법을 넘어, AI와 협업하는 새로운 워크플로를 제시하는 도서가 차별화 포인트\"", {
      x: 0.7, y: 5.1, w: 8.6, h: 0.35,
      fontSize: 11, fontFace: "Georgia", color: C.accent, italic: true,
      align: "center", margin: 0
    });

    addPageNum(slide, 4, TOTAL);
    setNotes(slide,
      "트렌드 인사이트입니다. 크게 세 가지 메가 트렌드가 관찰됩니다. " +
      "첫째, 생성형 AI 실전 활용 트렌드입니다. ChatGPT, Claude, Gemini 각 플랫폼의 특화된 실무 활용법을 " +
      "다루는 도서가 베스트셀러 상위권을 차지하고 있습니다. " +
      "둘째, AI 기반 개발 패러다임입니다. Vibe Coding, Agentic Coding, Harness Engineering 등 " +
      "AI와 함께 개발하는 새로운 방법론을 소개하는 도서가 부상하고 있습니다. " +
      "셋째, 교육 분야로의 AI 확산입니다. 2022 개정 교육과정과 맞물려 교사 대상 AI 에듀테크 활용서가 " +
      "꾸준한 수요를 형성하고 있습니다. 핵심 인사이트는 단순한 AI 사용법을 넘어 " +
      "AI와 협업하는 새로운 워크플로를 제시하는 도서가 차별화 포인트를 가진다는 점입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 5 — Publisher Competition
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "출판사별 경쟁 구도", "주요 출판사 포지셔닝 분석");

    const publishers = [
      { name: "한빛미디어", count: "7권", share: "28%", focus: "AI 엔지니어링, 교사 에듀테크", color: C.accent },
      { name: "골든래빗", count: "4권", share: "16%", focus: "AI 실전 활용, 수익화", color: C.darkBg },
      { name: "이지스퍼블리싱", count: "3권", share: "12%", focus: "입문서 · Do it! 시리즈", color: C.accentGold },
      { name: "앤써북 · 프리렉 외", count: "6권", share: "24%", focus: "교육 특화, 교사 대상", color: C.textMid },
    ];

    // Table header
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 1.5, w: 8.6, h: 0.4,
      fill: { color: C.darkBg }
    });
    slide.addText([
      { text: "출판사", options: { bold: true, fontSize: 11, fontFace: "Calibri", color: C.textLight } },
    ], { x: 0.9, y: 1.5, w: 1.5, h: 0.4, valign: "middle", margin: 0 });
    slide.addText("권수", { x: 2.5, y: 1.5, w: 0.8, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.textLight, bold: true, align: "center", valign: "middle", margin: 0 });
    slide.addText("점유율", { x: 3.4, y: 1.5, w: 0.8, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.textLight, bold: true, align: "center", valign: "middle", margin: 0 });
    slide.addText("주요 포커스", { x: 4.5, y: 1.5, w: 4.5, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.textLight, bold: true, valign: "middle", margin: 0 });

    publishers.forEach((p, i) => {
      const yBase = 1.95 + i * 0.55;
      const bgColor = i % 2 === 0 ? C.cardBg : C.lightBg;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 8.6, h: 0.5,
        fill: { color: bgColor }
      });
      slide.addText(p.name, {
        x: 0.9, y: yBase, w: 1.5, h: 0.5,
        fontSize: 12, fontFace: "Calibri", color: C.textDark, bold: true,
        valign: "middle", margin: 0
      });
      slide.addText(p.count, {
        x: 2.5, y: yBase, w: 0.8, h: 0.5,
        fontSize: 12, fontFace: "Calibri", color: C.textDark,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(p.share, {
        x: 3.4, y: yBase, w: 0.8, h: 0.5,
        fontSize: 12, fontFace: "Calibri", color: C.accent, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(p.focus, {
        x: 4.5, y: yBase, w: 4.5, h: 0.5,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        valign: "middle", margin: 0
      });
    });

    // Insight box
    addCard(slide, pres, 0.7, 4.2, 8.6, 1.1, C.accentGold);
    slide.addText([
      { text: "💡 Insight  ", options: { bold: true, fontSize: 12, fontFace: "Calibri", color: C.accentGold } },
      { text: "한빛미디어가 28%로 시장을 선도. 골든래빗은 '이게 되네?' 시리즈로 AI 실전 활용 분야에서 강력한 브랜드 구축. 교육 특화 출판사(앤써북, 프리렉, 사회평론아카데미)가 틈새시장 공략 중.", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark } },
    ], {
      x: 1.0, y: 4.3, w: 8.0, h: 0.9,
      valign: "middle", margin: 0
    });

    addPageNum(slide, 5, TOTAL);
    setNotes(slide,
      "출판사별 경쟁 구도입니다. 한빛미디어가 7권으로 28%의 점유율을 차지하며 시장을 선도하고 있습니다. " +
      "특히 AI 엔지니어링과 교사 에듀테크 분야에서 강력한 라인업을 구축하고 있습니다. " +
      "골든래빗은 '이게 되네?' 시리즈를 통해 AI 실전 활용 분야에서 4권을 배출하며 강력한 브랜드 파워를 보여주고 있습니다. " +
      "이지스퍼블리싱은 'Do it!' '된다!' 시리즈로 입문서 시장을 공략 중이고, " +
      "교육 특화 출판사들이 AI 에듀테크 틈새시장을 적극 공략하고 있습니다. " +
      "주목할 점은 전통적인 IT 출판사뿐 아니라 교육 전문 출판사까지 AI 도서 시장에 진입하고 있다는 것입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 6 — TOP 5 Books
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "TOP 10 베스트셀러 분석", "판매지수 기준 주요 도서");

    const books = [
      { rank: "1", title: "혼자 공부하는 바이브 코딩", author: "조태호", publisher: "한빛미디어", score: "80,778" },
      { rank: "2", title: "이게 되네? 제미나이 완전 미친 활용법", author: "오힘찬", publisher: "골든래빗", score: "77,754" },
      { rank: "3", title: "AI 시대의 질문력, 프롬프트 엔지니어링", author: "류한석", publisher: "코리아닷컴", score: "77,439" },
      { rank: "4", title: "된다! 하루 만에 끝내는 제미나이", author: "권서림", publisher: "이지스퍼블리싱", score: "75,963" },
      { rank: "5", title: "요즘 교사를 위한 AI 수업 활용", author: "박진환 외", publisher: "한빛미디어", score: "82,788" },
    ];

    // Header
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 1.5, w: 8.6, h: 0.35,
      fill: { color: C.darkBg }
    });
    const hdrOpts = { fontSize: 10, fontFace: "Calibri", color: C.textLight, bold: true, valign: "middle", margin: 0 };
    slide.addText("순위", { x: 0.85, y: 1.5, w: 0.5, h: 0.35, ...hdrOpts, align: "center" });
    slide.addText("도서명", { x: 1.5, y: 1.5, w: 3.8, h: 0.35, ...hdrOpts });
    slide.addText("저자", { x: 5.3, y: 1.5, w: 1.2, h: 0.35, ...hdrOpts });
    slide.addText("출판사", { x: 6.5, y: 1.5, w: 1.2, h: 0.35, ...hdrOpts });
    slide.addText("판매지수", { x: 7.8, y: 1.5, w: 1.2, h: 0.35, ...hdrOpts, align: "center" });

    books.forEach((b, i) => {
      const yBase = 1.9 + i * 0.48;
      const bgColor = i % 2 === 0 ? C.cardBg : C.lightBg;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 8.6, h: 0.43,
        fill: { color: bgColor }
      });
      // Rank circle
      slide.addShape(pres.shapes.OVAL, {
        x: 0.85, y: yBase + 0.07, w: 0.3, h: 0.3,
        fill: { color: i === 0 ? C.accentGold : C.border }
      });
      slide.addText(b.rank, {
        x: 0.85, y: yBase + 0.07, w: 0.3, h: 0.3,
        fontSize: 10, fontFace: "Calibri", color: i === 0 ? C.textLight : C.textDark, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(b.title, {
        x: 1.5, y: yBase, w: 3.8, h: 0.43,
        fontSize: 11, fontFace: "Calibri", color: C.textDark, bold: i === 0,
        valign: "middle", margin: 0
      });
      slide.addText(b.author, { x: 5.3, y: yBase, w: 1.2, h: 0.43, fontSize: 10, fontFace: "Calibri", color: C.textMid, valign: "middle", margin: 0 });
      slide.addText(b.publisher, { x: 6.5, y: yBase, w: 1.2, h: 0.43, fontSize: 10, fontFace: "Calibri", color: C.textMid, valign: "middle", margin: 0 });
      slide.addText(b.score, { x: 7.8, y: yBase, w: 1.2, h: 0.43, fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true, align: "center", valign: "middle", margin: 0 });
    });

    addPageNum(slide, 6, TOTAL);
    setNotes(slide,
      "TOP 10 베스트셀러 분석입니다. 판매지수 기준 상위 5위 도서를 살펴보면, " +
      "1위는 한빛미디어의 '혼자 공부하는 바이브 코딩'으로 8만 이상의 판매지수를 기록하며 압도적인 인기를 보여주고 있습니다. " +
      "2위와 4위는 각각 골든래빗과 이지스퍼블리싱의 제미나이 활용서로, 구글 제미나이에 대한 높은 관심을 반영합니다. " +
      "3위 '프롬프트 엔지니어링'은 프롬프트 작성법이라는 기초 수요를 잘 공략한 사례입니다. " +
      "5위는 교사 대상 AI 도서로, 교육 시장의 잠재력을 보여줍니다. " +
      "흥미로운 점은 상위 5위 중 4권이 AI 활용서라는 점입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 7 — AI Books Deep Dive
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "AI 도서 집중 분석", "카테고리별 세부 분석");

    const categories = [
      {
        cat: "플랫폼 실전 활용", pct: "45%",
        examples: "Claude 올인원, Gemini 활용법 81제,\nChatGPT · Gemini · Claude 3대장",
        color: C.accent
      },
      {
        cat: "AI 개발/엔지니어링", pct: "25%",
        examples: "Claude Code 마스터, Harness Engineering,\nAgentic Coding, Vibe Coding 1인 창업",
        color: C.darkBg
      },
      {
        cat: "교육(AI 에듀테크)", pct: "25%",
        examples: "교사를 위한 AI 바이브 코딩,\nAI 수업 활용 가이드, 에듀테크 5대장",
        color: C.accentGold
      },
      {
        cat: "AI 반도체/인프라", pct: "5%",
        examples: "한눈에 보는 AI 반도체 산업",
        color: C.textMid
      },
    ];

    categories.forEach((c, i) => {
      const xBase = 0.7 + (i % 2) * 4.4;
      const yBase = 1.5 + Math.floor(i / 2) * 1.85;

      addCard(slide, pres, xBase, yBase, 4.2, 1.65, c.color);

      // Category colored dot
      slide.addShape(pres.shapes.RECTANGLE, {
        x: xBase + 0.2, y: yBase + 0.2, w: 0.8, h: 0.3,
        fill: { color: c.color }
      });
      slide.addText(c.cat, {
        x: xBase + 0.2, y: yBase + 0.2, w: 0.8, h: 0.3,
        fontSize: 8, fontFace: "Calibri", color: C.textLight, bold: true,
        align: "center", valign: "middle", margin: 0
      });

      // Percentage - big number
      slide.addText(c.pct, {
        x: xBase + 1.2, y: yBase + 0.15, w: 1.2, h: 0.45,
        fontSize: 24, fontFace: "Georgia", color: c.color, bold: true,
        margin: 0
      });

      // Examples
      slide.addText(c.examples, {
        x: xBase + 0.2, y: yBase + 0.6, w: 3.8, h: 0.9,
        fontSize: 10, fontFace: "Calibri", color: C.textMid,
        margin: 0
      });
    });

    addPageNum(slide, 7, TOTAL);
    setNotes(slide,
      "AI 도서를 카테고리별로 세분화하면 네 가지로 분류됩니다. " +
      "가장 큰 비중을 차지하는 것은 ChatGPT, Claude, Gemini 등 플랫폼별 실전 활용서로 45%를 차지합니다. " +
      "다음으로 AI 개발 및 엔지니어링 분야가 25%, 교육 AI 에듀테크 분야가 25%로 동률을 이루고 있습니다. " +
      "AI 반도체 산업 도서가 5%를 차지합니다. " +
      "주목할 점은 AI 활용서와 AI 개발서의 경계가 모호해지고 있다는 것입니다. " +
      "Claude Code 같은 도구는 개발자를 위한 것이면서 동시에 비개발자도 사용할 수 있기 때문입니다. " +
      "이는 신규 도서 기획에서 중요한 시사점을 제공합니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 8 — Price & Rating Analysis
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "가격 및 평점 분석", "가격대별 분포와 독자 만족도");

    // Price range cards
    const ranges = [
      { range: "~ 19,000원", count: "5권", avgRating: "9.8", color: C.accent },
      { range: "20,000 ~ 24,000원", count: "8권", avgRating: "9.9", color: C.darkBg },
      { range: "25,000 ~ 29,000원", count: "5권", avgRating: "9.7", color: C.accentGold },
      { range: "30,000원 ~", count: "2권", avgRating: "9.8", color: C.textMid },
    ];

    slide.addText("가격대별 분포", {
      x: 0.7, y: 1.5, w: 4.3, h: 0.35,
      fontSize: 14, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0
    });

    ranges.forEach((r, i) => {
      const yBase = 1.95 + i * 0.55;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 4.3, h: 0.45,
        fill: { color: i % 2 === 0 ? C.cardBg : C.lightBg }
      });
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 0.05, h: 0.45,
        fill: { color: r.color }
      });
      slide.addText(r.range, { x: 1.0, y: yBase, w: 1.4, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.textDark, bold: true, valign: "middle", margin: 0 });
      slide.addText(r.count, { x: 2.5, y: yBase, w: 0.6, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.textDark, align: "center", valign: "middle", margin: 0 });
      slide.addText(`⭐ ${r.avgRating}`, { x: 3.2, y: yBase, w: 1.5, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.accentGold, valign: "middle", margin: 0 });
    });

    // Key insight right side
    addCard(slide, pres, 5.3, 1.5, 4.2, 3.5, C.accentGold);
    slide.addText("Price-Quality\nCorrelation", {
      x: 5.6, y: 1.7, w: 3.6, h: 0.6,
      fontSize: 16, fontFace: "Georgia", color: C.accentGold, bold: true, margin: 0
    });
    slide.addText([
      { text: "• ", options: { bold: true, color: C.accent } },
      { text: "가격과 평점 간 유의미한 상관관계 없음", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accent } },
      { text: "20,000~24,000원 구간이 가장 많은 도서 집중 (32%)", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accent } },
      { text: "전 구간 평균 평점 9.8점으로 전반적 만족도 높음", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "", options: { fontSize: 6, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accent } },
      { text: "권장 가격대: 20,000~25,000원", options: { fontSize: 12, fontFace: "Calibri", color: C.textDark, bold: true } },
    ], {
      x: 5.6, y: 2.4, w: 3.6, h: 2.3,
      valign: "top", margin: 0
    });

    addPageNum(slide, 8, TOTAL);
    setNotes(slide,
      "가격 및 평점 분석입니다. 가격대별로 살펴보면 2만 원에서 2만 4천 원 구간에 가장 많은 도서가 집중되어 있습니다. " +
      "흥미로운 점은 가격과 평점 간에 유의미한 상관관계가 없다는 것입니다. " +
      "즉, 비싼 책이 더 좋은 평가를 받지도, 싼 책이 더 나쁜 평가를 받지도 않습니다. " +
      "전 구간 평균 평점이 9.8점으로 매우 높아 IT 모바일 베스트셀러 시장의 독자 만족도가 전반적으로 높습니다. " +
      "이를 바탕으로 신규 도서의 권장 가격대는 2만 원에서 2만 5천 원 선이 적절할 것으로 판단됩니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 9 — Reader Needs Analysis
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "독자 니즈 분석", "리뷰 데이터 기반 인사이트");

    const needs = [
      { icon: "1", title: "실무 즉시 활용", desc: "이론보다 '바로 써먹는' 실전 예제에 대한 니즈가 압도적으로 높음", color: C.accent },
      { icon: "2", title: "비개발자 진입 장벽 해소", desc: "코딩을 몰라도 따라 할 수 있는 낮은 진입 장벽이 핵심 성공 요인", color: C.darkBg },
      { icon: "3", title: "멀티 플랫폼 비교", desc: "ChatGPT vs Gemini vs Claude 비교 분석에 대한 관심 지속적", color: C.accentGold },
      { icon: "4", title: "수익화 · 창업 연계", desc: "AI 활용을 넘어 실제 수익과 창업으로 연결하는 실전 전략 수요 증가", color: C.textMid },
    ];

    needs.forEach((n, i) => {
      const xBase = 0.7 + (i % 2) * 4.4;
      const yBase = 1.5 + Math.floor(i / 2) * 1.85;

      addCard(slide, pres, xBase, yBase, 4.2, 1.65, n.color);

      // Number circle
      slide.addShape(pres.shapes.OVAL, {
        x: xBase + 0.2, y: yBase + 0.2, w: 0.4, h: 0.4,
        fill: { color: n.color }
      });
      slide.addText(n.icon, {
        x: xBase + 0.2, y: yBase + 0.2, w: 0.4, h: 0.4,
        fontSize: 14, fontFace: "Georgia", color: C.textLight, bold: true,
        align: "center", valign: "middle", margin: 0
      });

      slide.addText(n.title, {
        x: xBase + 0.75, y: yBase + 0.2, w: 3.2, h: 0.4,
        fontSize: 14, fontFace: "Georgia", color: C.textDark, bold: true,
        valign: "middle", margin: 0
      });

      slide.addText(n.desc, {
        x: xBase + 0.2, y: yBase + 0.75, w: 3.8, h: 0.7,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        margin: 0
      });
    });

    addPageNum(slide, 9, TOTAL);
    setNotes(slide,
      "독자 니즈 분석입니다. 리뷰 데이터를 분석한 결과 네 가지 핵심 니즈가 도출되었습니다. " +
      "첫째, 실무 즉시 활용에 대한 니즈가 압도적으로 높습니다. 이론보다는 '바로 써먹는' 실전 예제를 원합니다. " +
      "둘째, 비개발자의 진입 장벽을 낮춰주는 도서가 인기를 끌고 있습니다. " +
      "'코딩을 몰라도 된다'는 메시지가 중요한 성공 요인입니다. " +
      "셋째, ChatGPT, Gemini, Claude 간 비교 분석에 대한 관심이 지속적입니다. " +
      "넷째, AI 활용을 넘어 실제 수익화와 창업으로 연결하는 실전 전략에 대한 수요가 증가하고 있습니다. " +
      "이러한 니즈를 종합적으로 충족하는 도서 기획이 필요합니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 10 — Differentiation Strategy
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "경쟁 도서 차별화 전략", "시장 갭 분석 및 포지셔닝");

    // Gap analysis
    slide.addText("시장 갭 (Market Gap)", {
      x: 0.7, y: 1.5, w: 4.3, h: 0.35,
      fontSize: 14, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0
    });

    const gaps = [
      { gap: "AI 도구별 '언제 무엇을 써야 하는가'에 대한 통합 가이드 부재", color: C.accent },
      { gap: "초보자 대상 'AI 업무 자동화 엔드투엔드' 실전서 부족", color: C.darkBg },
      { gap: "AI 리터러시부터 실전 활용까지 '올인원' 코스 부재", color: C.accentGold },
    ];

    gaps.forEach((g, i) => {
      const yBase = 1.95 + i * 0.5;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 4.3, h: 0.4,
        fill: { color: C.cardBg }
      });
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 0.05, h: 0.4,
        fill: { color: g.color }
      });
      slide.addText(g.gap, {
        x: 1.0, y: yBase, w: 3.8, h: 0.4,
        fontSize: 10, fontFace: "Calibri", color: C.textDark,
        valign: "middle", margin: 0
      });
    });

    // Our positioning
    addCard(slide, pres, 5.3, 1.5, 4.2, 3.5, C.accent);
    slide.addText("Our\nPositioning", {
      x: 5.5, y: 1.7, w: 3.7, h: 0.7,
      fontSize: 18, fontFace: "Georgia", color: C.accent, bold: true, margin: 0
    });

    const posItems = [
      "AI 3대 플랫폼 통합 실전 가이드",
      "초보자 맞춤형 '업무 자동화' 중심",
      "실습 프로젝트 10+ 포함",
      "비개발자 진입 장벽 최소화",
      "수익화·창업 연계 콘텐츠",
    ];

    slide.addText(posItems.map((item, i) => ({
      text: `✓  ${item}`,
      options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: i < posItems.length - 1, bold: i === 0 }
    })), {
      x: 5.5, y: 2.5, w: 3.7, h: 2.2,
      valign: "top", margin: 0
    });

    addPageNum(slide, 10, TOTAL);
    setNotes(slide,
      "경쟁 도서 차별화 전략입니다. 시장 갭 분석 결과 세 가지 주요 기회 영역이 발견되었습니다. " +
      "첫째, AI 도구별로 언제 무엇을 써야 하는지에 대한 통합 가이드가 부재합니다. " +
      "둘째, 초보자를 위한 AI 업무 자동화 엔드투엔드 실전서가 부족합니다. " +
      "셋째, AI 리터러시부터 실전 활용까지의 올인원 코스가 없습니다. " +
      "이에 따른 우리의 포지셔닝은 AI 3대 플랫폼 통합 실전 가이드, 초보자 맞춤형 업무 자동화 중심, " +
      "10개 이상의 실습 프로젝트 포함, 비개발자 진입 장벽 최소화, 수익화 및 창업 연계 콘텐츠로 차별화하겠습니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 11 — New Book: Topic Proposal
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "신규 도서 제안 — 주제 선정", "AI 3대장 업무 자동화 올인원 가이드");

    // Book title card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 1.5, w: 8.6, h: 1.2,
      fill: { color: C.darkBg }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 1.5, w: 0.08, h: 1.2,
      fill: { color: C.accentGold }
    });
    slide.addText("제안 도서명", {
      x: 1.1, y: 1.55, w: 2, h: 0.3,
      fontSize: 9, fontFace: "Calibri", color: C.textMid, margin: 0
    });
    slide.addText("AI 3대장 업무 자동화 올인원 가이드", {
      x: 1.1, y: 1.85, w: 8, h: 0.45,
      fontSize: 22, fontFace: "Georgia", color: C.textLight, bold: true, margin: 0
    });
    slide.addText("ChatGPT · Gemini · Claude로 하루 8시간을 1시간으로 줄이는 실전 노하우", {
      x: 1.1, y: 2.35, w: 8, h: 0.3,
      fontSize: 11, fontFace: "Calibri", color: C.accentGold, italic: true, margin: 0
    });

    // Key differentiators
    slide.addText("핵심 차별점", {
      x: 0.7, y: 2.9, w: 4.3, h: 0.35,
      fontSize: 14, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0
    });

    const diffs = [
      { label: "통합 접근법", desc: "3개 AI 도구를 상황별로 비교하며 '최적의 도구 선택법' 제시" },
      { label: "업무 자동화 중심", desc: "기획·마케팅·개발·디자인 전 영역 엔드투엔드 자동화" },
      { label: "초보자 친화적", desc: "프롬프트 기본기부터 실전 프로젝트까지 단계별 학습" },
    ];

    diffs.forEach((d, i) => {
      const yBase = 3.35 + i * 0.7;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 4.3, h: 0.6,
        fill: { color: C.cardBg },
        shadow: thinShadow()
      });
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 0.05, h: 0.6,
        fill: { color: C.accent }
      });
      slide.addText(d.label, {
        x: 1.0, y: yBase + 0.02, w: 3.8, h: 0.28,
        fontSize: 12, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
      });
      slide.addText(d.desc, {
        x: 1.0, y: yBase + 0.28, w: 3.8, h: 0.28,
        fontSize: 10, fontFace: "Calibri", color: C.textMid, margin: 0
      });
    });

    // Target reader card
    addCard(slide, pres, 5.3, 2.9, 4.2, 2.1, C.accentGold);
    slide.addText("Target Reader", {
      x: 5.5, y: 3.0, w: 3.7, h: 0.35,
      fontSize: 13, fontFace: "Georgia", color: C.accentGold, bold: true, margin: 0
    });
    slide.addText([
      { text: "• ", options: { bold: true, color: C.accentGold } },
      { text: "AI에 관심 있지만 막막한 직장인", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accentGold } },
      { text: "여러 AI 도구 중 선택에 어려움을 겪는 초보자", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accentGold } },
      { text: "업무 효율을 극대화하려는 예비 창업가", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark, breakLine: true } },
      { text: "• ", options: { bold: true, color: C.accentGold } },
      { text: "바이브 코딩으로 나만의 서비스를 만들고 싶은 비개발자", options: { fontSize: 11, fontFace: "Calibri", color: C.textDark } },
    ], {
      x: 5.5, y: 3.4, w: 3.7, h: 1.5,
      valign: "top", margin: 0
    });

    addPageNum(slide, 11, TOTAL);
    setNotes(slide,
      "신규 도서 제안 주제입니다. 제안 도서명은 'AI 3대장 업무 자동화 올인원 가이드'로, " +
      "ChatGPT, Gemini, Claude를 활용해 하루 8시간을 1시간으로 줄이는 실전 노하우를 담겠습니다. " +
      "핵심 차별점은 세 가지입니다. 첫째, 통합 접근법으로 3개 AI 도구를 상황별로 비교하며 최적의 도구 선택법을 제시합니다. " +
      "둘째, 업무 자동화에 방점을 두고 기획, 마케팅, 개발, 디자인 전 영역의 엔드투엔드 자동화를 다룹니다. " +
      "셋째, 프롬프트 기본기부터 실전 프로젝트까지 단계별 학습이 가능한 초보자 친화적 구성입니다. " +
      "타겟 독자는 AI에 관심 있지만 막막한 직장인, 여러 AI 도구 중 선택에 어려움을 겪는 초보자, " +
      "업무 효율을 극대화하려는 예비 창업가, 그리고 바이브 코딩으로 나만의 서비스를 만들고 싶은 비개발자입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 12 — Content Strategy
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "콘텐츠 구성 전략", "목차 및 분량 구성");

    // Chapter overview in table format
    const chapters = [
      { ch: "01", title: "AI 3대장 완전 정복", pages: "~40p", content: "ChatGPT · Gemini · Claude 특징부터 활용법까지" },
      { ch: "02", title: "프롬프트 엔지니어링 마스터", pages: "~35p", content: "상황별 프롬프트 패턴 & 최적화 전략" },
      { ch: "03", title: "업무 자동화 실전 프로젝트", pages: "~60p", content: "기획·마케팅·개발·디자인 10+ 프로젝트" },
      { ch: "04", title: "AI 바이브 코딩 with 클로드", pages: "~40p", content: "비개발자 맞춤형 웹앱 제작 워크플로" },
      { ch: "05", title: "AI 수익화 & 1인 창업", pages: "~30p", content: "AI 기반 비즈니스 모델과 실행 전략" },
    ];

    // Header
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 1.5, w: 8.6, h: 0.35,
      fill: { color: C.darkBg }
    });
    const hdr = { fontSize: 10, fontFace: "Calibri", color: C.textLight, bold: true, valign: "middle", margin: 0 };
    slide.addText("파트", { x: 0.85, y: 1.5, w: 0.5, h: 0.35, ...hdr, align: "center" });
    slide.addText("챕터명", { x: 1.5, y: 1.5, w: 2.5, h: 0.35, ...hdr });
    slide.addText("분량", { x: 4.0, y: 1.5, w: 0.8, h: 0.35, ...hdr, align: "center" });
    slide.addText("주요 내용", { x: 5.0, y: 1.5, w: 4.0, h: 0.35, ...hdr });

    chapters.forEach((ch, i) => {
      const yBase = 1.9 + i * 0.5;
      const bgColor = i % 2 === 0 ? C.cardBg : C.lightBg;
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.7, y: yBase, w: 8.6, h: 0.45,
        fill: { color: bgColor }
      });
      slide.addText(ch.ch, {
        x: 0.85, y: yBase, w: 0.5, h: 0.45,
        fontSize: 12, fontFace: "Georgia", color: C.accent, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(ch.title, {
        x: 1.5, y: yBase, w: 2.5, h: 0.45,
        fontSize: 11, fontFace: "Calibri", color: C.textDark, bold: true,
        valign: "middle", margin: 0
      });
      slide.addText(ch.pages, {
        x: 4.0, y: yBase, w: 0.8, h: 0.45,
        fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true,
        align: "center", valign: "middle", margin: 0
      });
      slide.addText(ch.content, {
        x: 5.0, y: yBase, w: 4.0, h: 0.45,
        fontSize: 10, fontFace: "Calibri", color: C.textMid,
        valign: "middle", margin: 0
      });
    });

    // Total summary
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: 4.5, w: 8.6, h: 0.45,
      fill: { color: C.accentLight }
    });
    slide.addText("예상 전체 분량: 280~300페이지  |  실습 프로젝트: 12개  |  난이도: 초급~중급", {
      x: 0.7, y: 4.5, w: 8.6, h: 0.45,
      fontSize: 11, fontFace: "Calibri", color: C.textDark, bold: true,
      align: "center", valign: "middle", margin: 0
    });

    // Free QR/extra value
    slide.addText("✓ 부록: 실습 프로젝트 소스 코드 및 프롬프트 템플릿 제공  |  ✓ 저자 직강 유튜브 강의 연계", {
      x: 0.7, y: 4.95, w: 8.6, h: 0.5,
      fontSize: 10, fontFace: "Calibri", color: C.textMid, italic: true,
      align: "center", valign: "middle", margin: 0
    });

    addPageNum(slide, 12, TOTAL);
    setNotes(slide,
      "콘텐츠 구성 전략입니다. 총 5개 파트, 280에서 300페이지 분량으로 기획했습니다. " +
      "1장에서는 AI 3대장인 ChatGPT, Gemini, Claude의 특징부터 실전 활용법까지 다룹니다. " +
      "2장은 프롬프트 엔지니어링 마스터로 상황별 프롬프트 패턴과 최적화 전략을 담습니다. " +
      "3장은 핵심인 업무 자동화 실전 프로젝트로 10개 이상의 엔드투엔드 프로젝트를 포함합니다. " +
      "4장은 AI 바이브 코딩으로 비개발자도 웹앱을 만들 수 있도록 안내합니다. " +
      "5장은 AI 수익화와 1인 창업 전략으로 구성했습니다. " +
      "실습 프로젝트 12개와 부록으로 소스 코드 및 프롬프트 템플릿을 제공하고, 저자 직강 유튜브 강의와 연계할 계획입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 13 — Marketing Strategy
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "마케팅 전략", "채널별 프로모션 계획");

    const strategies = [
      {
        channel: "SNS · 커뮤니티",
        tactics: "IT/스타트업 커뮤니티 타겟팅\nAI 관련 오픈채팅방·네이버 카페\n인스타그램 릴스 · 숏폼 홍보",
        color: C.accent
      },
      {
        channel: "유튜브 · 강의",
        tactics: "저자 직강 유튜브 강의 연계\n챕터별 미리보기 영상 제작\nAI 크리에이터 협업 리뷰",
        color: C.darkBg
      },
      {
        channel: "서점 · 온라인",
        tactics: "YES24 · 교보문고 IT 신간 코너\nMD 추천 코스터 · 배너 광고\n전자책(eBook) 동시 출간",
        color: C.accentGold
      },
      {
        channel: "기업 · 기관",
        tactics: "기업체 AI 교육 패키지 제안\n공공기관 디지털 역량 교육 과정\n대학 AI 특강 연계",
        color: C.textMid
      },
    ];

    strategies.forEach((s, i) => {
      const xBase = 0.7 + (i % 2) * 4.4;
      const yBase = 1.5 + Math.floor(i / 2) * 1.85;

      addCard(slide, pres, xBase, yBase, 4.2, 1.65, s.color);

      slide.addText(s.channel, {
        x: xBase + 0.2, y: yBase + 0.2, w: 3.8, h: 0.35,
        fontSize: 14, fontFace: "Georgia", color: s.color, bold: true, margin: 0
      });

      slide.addText(s.tactics, {
        x: xBase + 0.2, y: yBase + 0.65, w: 3.8, h: 0.85,
        fontSize: 11, fontFace: "Calibri", color: C.textMid,
        margin: 0
      });
    });

    addPageNum(slide, 13, TOTAL);
    setNotes(slide,
      "마케팅 전략입니다. 네 가지 주요 채널을 통해 프로모션을 진행할 계획입니다. " +
      "첫째, SNS 및 커뮤니티 채널을 통해 IT 스타트업 커뮤니티를 타겟팅하고, " +
      "AI 관련 오픈채팅방과 네이버 카페, 인스타그램 릴스 등 숏폼 콘텐츠로 홍보합니다. " +
      "둘째, 유튜브 강의 연계로 저자 직강 콘텐츠와 챕터별 미리보기 영상을 제작하고 AI 크리에이터와 협업 리뷰를 진행합니다. " +
      "셋째, YES24와 교보문고 IT 신간 코너에 입점하고 MD 추천과 배너 광고를 진행하며 전자책을 동시 출간합니다. " +
      "넷째, 기업체 AI 교육 패키지, 공공기관 디지털 역량 교육, 대학 AI 특강 등 B2B 채널도 공략합니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 14 — Timeline & P&L
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.lightBg };
    addSlideHeader(slide, pres, "예상 일정 및 손익 구조", "출간 로드맵 및 수익 예측");

    // Timeline
    slide.addText("출간 로드맵", {
      x: 0.7, y: 1.5, w: 4.3, h: 0.35,
      fontSize: 14, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0
    });

    const milestones = [
      { month: "1~2M", task: "원고 집필", status: "필수", color: C.accent },
      { month: "3M", task: "내부 검토 · 윤문", status: "필수", color: C.accent },
      { month: "4M", task: "표지 디자인 · 판형", status: "필수", color: C.darkBg },
      { month: "5M", task: "인쇄 · 유통 준비", status: "필수", color: C.darkBg },
      { month: "6M", task: "정식 출간", status: "목표", color: C.accentGold },
    ];

    // Timeline visual
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: 1.9, w: 0.04, h: 2.6,
      fill: { color: C.divider }
    });

    milestones.forEach((m, i) => {
      const yBase = 1.95 + i * 0.5;
      // Dot
      slide.addShape(pres.shapes.OVAL, {
        x: 0.82, y: yBase + 0.08, w: 0.2, h: 0.2,
        fill: { color: m.color }
      });
      slide.addText(m.month, {
        x: 1.2, y: yBase, w: 0.8, h: 0.35,
        fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true,
        valign: "middle", margin: 0
      });
      slide.addText(m.task, {
        x: 2.1, y: yBase, w: 2.5, h: 0.35,
        fontSize: 11, fontFace: "Calibri", color: C.textDark,
        valign: "middle", margin: 0
      });
    });

    // P&L card
    addCard(slide, pres, 5.3, 1.5, 4.2, 3.5, C.accentGold);
    slide.addText("예상 손익 구조", {
      x: 5.5, y: 1.7, w: 3.7, h: 0.35,
      fontSize: 13, fontFace: "Georgia", color: C.accentGold, bold: true, margin: 0
    });

    const plItems = [
      { label: "예상 정가", value: "22,000원" },
      { label: "초판 발행 부수", value: "3,000부" },
      { label: "예상 매출 (초판)", value: "66,000,000원" },
      { label: "인쇄비 (예상)", value: "~15,000,000원" },
      { label: "인세 (10%)", value: "~6,600,000원" },
      { label: "마케팅비", value: "~5,000,000원" },
      { label: "예상 손익", value: "약 39,000,000원" },
    ];

    plItems.forEach((p, i) => {
      const yBase = 2.15 + i * 0.38;
      slide.addText(p.label, {
        x: 5.5, y: yBase, w: 2.0, h: 0.35,
        fontSize: 10, fontFace: "Calibri", color: C.textMid,
        valign: "middle", margin: 0
      });
      slide.addText(p.value, {
        x: 7.2, y: yBase, w: 2.0, h: 0.35,
        fontSize: 11, fontFace: "Calibri", color: i === plItems.length - 1 ? C.accentGold : C.textDark,
        bold: i === plItems.length - 1, align: "right", valign: "middle", margin: 0
      });
      if (i < plItems.length - 1) {
        slide.addShape(pres.shapes.RECTANGLE, {
          x: 5.5, y: yBase + 0.35, w: 3.7, h: 0.01,
          fill: { color: C.divider }
        });
      }
    });

    addPageNum(slide, 14, TOTAL);
    setNotes(slide,
      "예상 일정 및 손익 구조입니다. 출간 로드맵은 총 6개월을 목표로 합니다. " +
      "1~2개월 차에 원고 집필, 3개월 차에 내부 검토 및 윤문, " +
      "4개월 차에 표지 디자인과 판형 결정, 5개월 차에 인쇄 및 유통 준비, " +
      "6개월 차에 정식 출간하는 일정입니다. " +
      "예상 손익 구조를 살펴보면, 정가 22,000원, 초판 3,000부 기준으로 " +
      "예상 매출은 6,600만 원입니다. 인쇄비 약 1,500만 원, 인세 약 660만 원, " +
      "마케팅비 약 500만 원을 제외한 예상 손익은 약 3,900만 원입니다. " +
      "초판 완판 시 추가 수익이 예상되며, 전자책 출간을 통해 추가 수익원을 확보할 계획입니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  // SLIDE 15 — Closing (dark bg)
  // ═══════════════════════════════════════════════════════════
  {
    const slide = pres.addSlide();
    slide.background = { color: C.darkBg };

    // Decorative circle
    slide.addShape(pres.shapes.OVAL, {
      x: -2, y: -1.5, w: 5, h: 5,
      fill: { color: C.darkBg2, transparency: 60 }
    });
    slide.addShape(pres.shapes.OVAL, {
      x: 7, y: 3.5, w: 4, h: 4,
      fill: { color: C.darkBg2, transparency: 70 }
    });

    // Accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.8, y: 1.3, w: 0.08, h: 1.6,
      fill: { color: C.accentGold }
    });

    slide.addText("감사합니다", {
      x: 1.2, y: 1.4, w: 7, h: 0.7,
      fontSize: 36, fontFace: "Georgia", color: C.textLight, bold: true,
      margin: 0
    });

    slide.addText("Q&A", {
      x: 1.2, y: 2.2, w: 7, h: 0.6,
      fontSize: 20, fontFace: "Georgia", color: C.accentGold,
      margin: 0
    });

    slide.addText("데이터 기반 신규 도서 기획 제안 | ABC-RAG 프로젝트", {
      x: 1.2, y: 4.6, w: 7, h: 0.4,
      fontSize: 11, fontFace: "Calibri", color: C.textMid,
      margin: 0
    });

    setNotes(slide,
      "이상으로 신규 도서 기획 제안 발표를 마치겠습니다. " +
      "YES24 IT 모바일 베스트셀러 데이터 분석을 기반으로 한 AI 3대장 업무 자동화 올인원 가이드는 " +
      "현재 시장의 갭을 정확히 공략하는 차별화된 포지셔닝을 가지고 있습니다. " +
      "AI 도서 시장이 급성장하고 있는 지금이 진입에 최적의 타이밍입니다. " +
      "질문이나 의견 있으시면 자유롭게 말씀해 주시기 바랍니다. 감사합니다."
    );
  }

  // ═══════════════════════════════════════════════════════════
  //  WRITE FILE
  // ═══════════════════════════════════════════════════════════

  const outputPath = "C:\\documents\\26-1\\한신대ABC캠프-2026\\ABC-RAG\\outputs\\신규_도서_기획_제안서.pptx";
  await pres.writeFile({ fileName: outputPath });
  console.log("✅ Presentation saved to:", outputPath);
}

createPresentation().catch(err => {
  console.error("❌ Error:", err);
  process.exit(1);
});
