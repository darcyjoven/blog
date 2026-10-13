"""
中文转拼音的最小映射表。

为什么不用 pypinyin：本机 Python 3.14 移除了 ensurepip，装不了第三方包；
GitHub Actions 上虽然能装，但会引入不必要的网络依赖和版本漂移风险。
这里用固定映射表，结果确定、可审计、零依赖。

覆盖范围：blog 表 77 条标题/slug 中出现的全部 222 个汉字。
未收录的字在 slug 生成时会退回「ASCII 部分 + 页面 ID 后 8 位」，
不会报错，只是 URL 可读性差一些——所以忘了收录时 slug 变难看，
这是刻意的：宁可 URL 丑，也不要静默出错。

需要补字时：在下面加一行 `"字": "拼音",` 即可。
"""

PINYIN = {
    "一": "yi", "三": "san", "上": "shang", "下": "xia", "不": "bu",
    "与": "yu", "个": "ge", "临": "lin", "为": "wei", "义": "yi",
    "二": "er", "令": "ling", "件": "jian", "价": "jia", "传": "chuan",
    "作": "zuo", "使": "shi", "例": "li", "信": "xin", "修": "xiu",
    "光": "guang", "入": "ru", "全": "quan", "具": "ju", "册": "ce",
    "决": "jue", "准": "zhun", "函": "han", "分": "fen", "划": "hua",
    "制": "zhi", "办": "ban", "功": "gong", "加": "jia", "动": "dong",
    "包": "bao", "单": "dan", "南": "nan", "印": "yin", "原": "yuan",
    "发": "fa", "取": "qu", "口": "kou", "号": "hao", "同": "tong",
    "启": "qi", "员": "yuan", "周": "zhou", "命": "ming", "品": "pin",
    "固": "gu", "块": "kuai", "型": "xing", "基": "ji", "境": "jing",
    "增": "zeng", "处": "chu", "复": "fu", "失": "shi", "套": "tao",
    "字": "zi", "存": "cun", "完": "wan", "定": "ding", "实": "shi",
    "客": "ke", "密": "mi", "导": "dao", "嵌": "qian", "工": "gong",
    "常": "chang", "并": "bing", "序": "xu", "库": "ku", "开": "kai",
    "异": "yi", "式": "shi", "录": "lu", "待": "dai", "志": "zhi",
    "态": "tai", "总": "zong", "息": "xi", "成": "cheng", "户": "hu",
    "手": "shou", "打": "da", "护": "hu", "报": "bao", "指": "zhi",
    "损": "sun", "换": "huan", "据": "ju", "授": "shou", "接": "jie",
    "操": "cao", "效": "xiao", "数": "shu", "文": "wen", "料": "liao",
    "断": "duan", "新": "xin", "方": "fang", "日": "ri", "时": "shi",
    "明": "ming", "显": "xian", "更": "geng", "最": "zui", "期": "qi",
    "本": "ben", "权": "quan", "板": "ban", "构": "gou", "析": "xi",
    "架": "jia", "查": "cha", "标": "biao", "样": "yang", "核": "he",
    "格": "ge", "框": "kuang", "案": "an", "模": "mo", "次": "ci",
    "款": "kuan", "步": "bu", "段": "duan", "求": "qiu", "汇": "hui",
    "法": "fa", "波": "bo", "流": "liu", "测": "ce", "消": "xiao",
    "源": "yuan", "率": "lv", "环": "huan", "理": "li", "生": "sheng",
    "用": "yong", "番": "fan", "的": "de", "盈": "ying", "盘": "pan",
    "目": "mu", "码": "ma", "础": "chu", "磁": "ci", "示": "shi",
    "福": "fu", "程": "cheng", "空": "kong", "第": "di", "算": "suan",
    "管": "guan", "类": "lei", "系": "xi", "级": "ji", "线": "xian",
    "细": "xi", "结": "jie", "络": "luo", "统": "tong", "维": "wei",
    "编": "bian", "网": "wang", "置": "zhi", "耗": "hao", "能": "neng",
    "自": "zi", "致": "zhi", "般": "ban", "艺": "yi", "范": "fan",
    "茄": "qie", "莱": "lai", "行": "hang", "表": "biao", "要": "yao",
    "规": "gui", "览": "lan", "解": "jie", "言": "yan", "计": "ji",
    "记": "ji", "设": "she", "译": "yi", "试": "shi", "询": "xun",
    "语": "yu", "误": "wu", "请": "qing", "调": "tiao", "败": "bai",
    "账": "zhang", "购": "gou", "贷": "dai", "资": "zi", "路": "lu",
    "践": "jian", "转": "zhuan", "辑": "ji", "运": "yun", "近": "jin",
    "选": "xuan", "通": "tong", "速": "su", "逻": "luo", "配": "pei",
    "重": "zhong", "钟": "zhong", "银": "yin", "链": "lian", "锁": "suo",
    "错": "cuo", "问": "wen", "间": "jian", "集": "ji", "项": "xiang",
    "题": "ti", "高": "gao",

    # 预留：技术文章常用字，后续按需补
    "后": "hou", "前": "qian", "里": "li", "外": "wai", "大": "da",
    "小": "xiao", "多": "duo", "少": "shao", "上": "shang", "中": "zhong",
    "为": "wei", "从": "cong", "到": "dao", "或": "huo", "与": "yu",
    "如": "ru", "何": "he", "怎": "zen", "么": "me", "这": "zhe",
    "那": "na", "哪": "na", "个": "ge", "们": "men", "些": "xie",
    "点": "dian", "线": "xian", "面": "mian", "层": "ceng", "级": "ji",
    "型": "xing", "版": "ban", "端": "duan", "端": "duan", "项目": "xiang-mu",
    "项": "xiang", "测": "ce", "试": "shi", "运": "yun", "维": "wei",
    "护": "hu", "管": "guan", "理": "li", "配": "pei", "置": "zhi",
    "设": "she", "安": "an", "装": "zhuang", "卸": "xie", "载": "zai",
    "更": "geng", "新": "xin", "删": "shan", "除": "chu", "增": "zeng",
    "减": "jian", "查": "cha", "找": "zhao", "替": "ti", "换": "huan",
    "轮": "lun", "询": "xun", "拉": "la", "取": "qu", "推": "tui",
    "送": "song", "同": "tong", "步": "bu", "异": "yi", "常": "chang",
    "错": "cuo", "误": "wu", "警": "jing", "告": "gao", "提": "ti",
    "示": "shi", "权": "quan", "限": "xian", "认": "ren", "证": "zheng",
    "证": "zheng", "书": "shu", "钥": "yao", "匙": "shi", "加": "jia",
    "密": "mi", "编": "bian", "码": "ma", "解": "jie", "压": "ya",
    "缩": "suo", "字": "zi", "节": "jie", "符": "fu", "号": "hao",
    "进": "jin", "程": "cheng", "线": "xian", "程": "cheng", "序": "xu",
    "列": "lie", "表": "biao", "结": "jie", "构": "gou", "对": "dui",
    "象": "xiang", "属": "shu", "性": "xing", "状": "zhuang", "态": "tai",
    "标": "biao", "签": "qian", "分": "fen", "类": "lei", "组": "zu",
    "织": "zhi", "优": "you", "化": "hua", "缓": "huan", "存": "cun",
    "加": "jia", "载": "zai", "失": "shi", "败": "bai", "成": "cheng",
    "功": "gong", "错": "cuo", "误": "wu", "排": "pai", "除": "chu",
    "比": "bi", "较": "jiao", "替": "ti", "换": "huan", "临": "lin",
    "时": "shi", "间": "jian", "秒": "miao", "分": "fen", "钟": "zhong",
    "小": "xiao", "时": "shi", "本": "ben", "周": "zhou", "年": "nian",
    "月": "yue", "日": "ri", "过": "guo", "期": "qi", "限": "xian",
    "内": "nei", "外": "wai", "全": "quan", "部": "bu", "部": "bu",
    "分": "fen", "支": "zhi", "支": "zhi", "路": "lu", "径": "jing",
    "方": "fang", "案": "an", "例": "li", "如": "ru", "果": "guo",
    "则": "ze", "否": "fou", "是": "shi", "非": "fei", "必": "bi",
    "须": "xu", "应": "ying", "该": "gai", "可": "ke", "能": "neng",
    "会": "hui", "要": "yao", "想": "xiang", "需": "xu", "求": "qiu",
    "支": "zhi", "持": "chi", "提": "ti", "供": "gong", "允": "yun",
    "许": "xu", "禁": "jin", "止": "zhi", "避": "bi", "免": "mian",
    "建": "jian", "议": "yi", "方案": "fang-an", "比": "bi", "较": "jiao",
    "示": "shi", "范": "fan", "例": "li", "总": "zong", "结": "jie",
    "论": "lun", "综": "zong", "合": "he", "概": "gai", "括": "kuo",
    "要": "yao", "点": "dian", "关": "guan", "键": "jian", "核心": "he-xin",
    "心": "xin", "思": "si", "路": "lu", "考": "kao", "虑": "lv",
    "理": "li", "解": "jie", "释": "shi", "明": "ming", "确": "que",
    "定": "ding", "义": "yi", "规": "gui", "则": "ze", "约": "yue",
    "定": "ding", "参": "can", "考": "kao", "资": "zi", "料": "liao",
    "来": "lai", "源": "yuan", "版": "ban", "权": "quan", "授": "shou",
    "许": "xu", "禁": "jin", "止": "zhi", "非": "fei", "商": "shang",
    "业": "ye", "个": "ge", "人": "ren", "使": "shi", "公": "gong",
    "开": "kai", "私": "si", "密": "mi", "内": "nei", "部": "bu",
}


def to_pinyin(text: str) -> tuple:
    """
    中文转拼音。

    返回 (拼音串, 未收录字集合)。未收录的字会被跳过，
    调用方据此判断是否需要退回兜底方案。

    中英文之间会插入空格，让 `BDL集成java包` 得到 `BDL ji cheng java bao`
    而不是 `BDL ji chengjava bao`——后者虽然合法但难看，且词边界不清。
    """
    out, missing = [], set()
    prev_was_cn = False

    for ch in text:
        if ord(ch) < 128:
            # ASCII 字符：如果前一个字是中文，先断开
            if prev_was_cn and out and not out[-1].endswith(" "):
                out.append(" ")
            out.append(ch)
            prev_was_cn = False
            continue

        p = PINYIN.get(ch)
        if p:
            if out and not out[-1].endswith(" "):
                out.append(" ")
            out.append(p)
            prev_was_cn = True
        else:
            missing.add(ch)
            prev_was_cn = False

    return "".join(out), missing
