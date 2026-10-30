"""Рисование структурных схем преобразований средствами matplotlib."""
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch


def draw_scheme(blocks, arrows, title=None, size=(12, 3.5), box_w=1.9, box_h=0.8):
    """
    Построение структурной схемы из прямоугольных блоков и стрелок.

    Параметры
    ----------
    blocks : dict
        {имя: (x, y, текст)} — координаты центра блока и надпись.
    arrows : list of tuple
        [(откуда, куда, подпись)] — стрелки между блоками (подпись может быть '').
    """
    fig, ax = plt.subplots(figsize=size)
    for name, (x, y, text) in blocks.items():
        ax.add_patch(FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                                    boxstyle='round,pad=0.05', fc='#eef3fb', ec='#2b5797', lw=1.4))
        ax.text(x, y, text, ha='center', va='center', fontsize=10)
    for src, dst, label in arrows:
        (x0, y0, _), (x1, y1, _) = blocks[src], blocks[dst]
        # стрелка от правого края исходного блока к левому краю целевого
        start = (x0 + box_w/2 + 0.05, y0) if x1 > x0 else (x0, y0 - box_h/2 * (1 if y1 < y0 else -1))
        end = (x1 - box_w/2 - 0.05, y1) if x1 > x0 else (x1, y1 + box_h/2 * (1 if y1 < y0 else -1))
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle='->', lw=1.3, color='#333333'))
        if label:
            ax.text((start[0] + end[0])/2, (start[1] + end[1])/2 + 0.12, label,
                    ha='center', va='bottom', fontsize=9, color='#333333')
    xs = [b[0] for b in blocks.values()]
    ys = [b[1] for b in blocks.values()]
    ax.set_xlim(min(xs) - box_w, max(xs) + box_w)
    ax.set_ylim(min(ys) - box_h, max(ys) + box_h)
    ax.set_aspect('equal')
    ax.axis('off')
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig
