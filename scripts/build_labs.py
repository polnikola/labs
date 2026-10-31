"""Создание двух воспроизводимых комплектов по Description.docx."""
from pathlib import Path
import nbformat as nb
ROOT = Path(__file__).resolve().parents[1]
COMMON = '''%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, stats, special
import pywt
plt.rcParams.update({'figure.figsize': (12,4), 'figure.dpi': 100,
                     'axes.grid': True, 'grid.alpha': .25})
'''
def make(num, pc, lab, cells):
    folder=ROOT/f'n{num}_pc{pc}'
    folder.mkdir(exist_ok=True)
    n=nb.v4.new_notebook(cells=[nb.v4.new_markdown_cell(f'# Лабораторная работа №{lab}\n\nНомер по списку: **{num}**, ПК: **{pc}**, группа: **2**.\n\nВарианты таблиц выбираются по кругу: (номер−1) % число строк + 1. Для ЛР3–4 N=ПК+группа; N не является номером по списку.')])
    n.cells += [nb.v4.new_code_cell(COMMON+f'number={num}; pc={pc}; group=2\nrng=np.random.default_rng({num*100+pc})\n')]
    if lab == 3:
        cells = cells[:-1] + transient_cells() + cells[-1:]
    for kind, src in cells: n.cells.append((nb.v4.new_code_cell if kind=='c' else nb.v4.new_markdown_cell)(src.strip()))
    n.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
    nb.write(n,folder/f'lab{lab}.ipynb')
def lab1(num,pc):
    rice=num==10
    law='Райса' if rice else 'показательный'
    formula=r'Y=\sqrt{(\sigma Z_1+a)^2+(\sigma Z_2)^2}' if rice else r'Y=(Z_1^2+Z_2^2)/(2\lambda)'
    cells=[('m',rf'''## Равномерная и нормальная случайные величины
Конгруэнтный генератор: $s_{{k+1}}=(1664525s_k+1013904223)\bmod 2^{{32}}$, $U=(s+0.5)/2^{{32}}$.
Нормальная СВ получается произведением независимых релеевской и арксинусной СВ:
$Z_1=\sqrt{{-2\ln U_1}}\cos(2\pi U_2)$, $Z_2=\sqrt{{-2\ln U_1}}\sin(2\pi U_2)$; $X=\mu+\sigma Z$.
Здесь $\sigma=2$, $\mu=a=\lambda={num}$; $Z_1,Z_2$ стандартные нормальные.
Структура: **LCG → U₁,U₂ → радиус и фаза → Z₁,Z₂ → μ+σZ → X**.
Нормировка гистограмм: $\hat p(x_i)=n_i/(N\Delta x_i)$; аналитическая плотность рассчитывается в центрах интервалов.'''),('c','''size=50000; sigma=group; mu=number
state=123456789
u=np.empty(2*size)
for k in range(len(u)):
    state=(1664525*state+1013904223) % 2**32
    u[k]=(state+.5)/2**32
u1,u2=u[::2],u[1::2]
r=np.sqrt(-2*np.log(u1)); phase=2*np.pi*u2
z1,z2=r*np.cos(phase),r*np.sin(phase)
x=mu+sigma*z1
xlib=rng.normal(mu,sigma,size)
def compare(samples,labels,dist,title):
    edges=np.linspace(min(s.min() for s in samples),max(s.max() for s in samples),75)
    centers=(edges[1:]+edges[:-1])/2
    fig,ax=plt.subplots()
    for s,l in zip(samples,labels): ax.hist(s,bins=edges,density=True,histtype='step',label=l)
    ax.plot(centers,dist.pdf(centers),'k--',label='Аналитическая плотность')
    ax.set(xlabel='x',ylabel='p(x)',title=title); ax.legend(); plt.show()
compare([u1,rng.uniform(size=size)],['LCG','NumPy'],stats.uniform(),'Равномерное U(0,1)')
compare([x,xlib],['Бокс — Мюллер от LCG','NumPy'],stats.norm(mu,sigma),f'Нормальное: μ={mu}, σ={sigma}')
fig,ax=plt.subplots(); ax.plot(x[:150]); ax.set(xlabel='Отсчёт',ylabel='X',title='Реализация нормальной СВ'); plt.show()
print('Оценки нормальной СВ: среднее, дисперсия:',x.mean(),x.var(),'; теория:',mu,sigma**2)
print('Корреляция Z1,Z2:',np.corrcoef(z1,z2)[0,1])
'''),('m',rf'''## Вариант {(num-1)%8+1}: нормальное → {law}
$${formula}.$$
Структура: **Z₁,Z₂ → нелинейное преобразование → Y → гистограмма и моменты**.
''')]
    if rice:
        cells += [('m',r'''Для Райса $a=10$, $\sigma=2$, $b=a/\sigma=5$.
$$p(y)=\frac{y}{\sigma^2}\exp\left(-\frac{y^2+a^2}{2\sigma^2}\right)I_0(ay/\sigma^2),\quad y\ge0.$$
Параметр `loc` равен нулю: смещение a действует на одну квадратуру, а не на итоговую амплитуду.'''),('c', '''y=np.hypot(sigma*z1+number,sigma*z2)
dist=stats.rice(number/sigma,scale=sigma)
ylib=dist.rvs(size=size,random_state=rng)
compare([sigma*z1,sigma*z2],['Квадратура 1','Квадратура 2'],stats.norm(0,sigma),'Исходные нормальные квадратуры')
compare([y,ylib],['Свой алгоритм','SciPy rice'],dist,f'Райс: a={number}, σ={sigma}')
''')]
    else:
        cells += [('m',r'''$Z_1^2+Z_2^2\sim\chi^2_2$, поэтому $p(y)=\lambda e^{-\lambda y}$, $y\ge0$. Теория: $E[Y]=1/\lambda$, $D[Y]=1/\lambda^2$. Если исходные квадратуры имеют СКО σ, их сумму квадратов нужно дополнительно делить на σ².'''),('c','''y=(z1*z1+z2*z2)/(2*number)
dist=stats.expon(scale=1/number)
ylib=rng.exponential(1/number,size)
compare([sigma*z1,sigma*z2],['Квадратура 1','Квадратура 2'],stats.norm(0,sigma),'Исходные нормальные квадратуры')
compare([y,ylib],['Свой алгоритм','NumPy exponential'],dist,f'Показательное: λ={number}')
''')]
    cells += [('c','''print('Y: среднее / теория:',y.mean(),dist.mean())
print('Y: дисперсия / теория:',y.var(),dist.var())
fig,ax=plt.subplots(); ax.plot(y[:150]); ax.set(xlabel='Отсчёт',ylabel='Y',title='Выходная реализация'); plt.show()
'''),('m',f'''## Выводы
Получены равномерная, нормальная и {law.lower()} СВ; собственные алгоритмы сопоставлены с библиотечными и аналитической плотностью. Оценки моментов приведены выше, конечная выборка вызывает отклонения гистограмм от теории. Псевдослучайный LCG детерминирован, поэтому совпадение плотности само по себе не доказывает независимость.
''' + ('Распределение Райса описывает амплитуду узкополосного сигнала на фоне гауссовского шума: одна квадратура содержит детерминированную составляющую a.' if rice else 'Показательное распределение описывает мощность комплексного гауссовского шума в радиоприёмнике (сумму квадратов двух независимых квадратур).'))]
    make(num,pc,1,cells)
def lab2(num,pc):
    triangular=num==10
    desc=r'R(\tau)=\max(1-|\tau|/l,0)' if triangular else r'R(\tau)=\cos(10\tau/l)e^{-(\tau/l)^2/2}'
    expr='np.maximum(1-np.abs(tau)/l,0)' if triangular else 'np.cos(10*tau/l)*np.exp(-.5*(tau/l)**2)'
    make(num,pc,2,[('m',rf'''## Формирование процесса с заданной КФ
Вариант {(num-1)%4+1}: ${desc}$, $l_1={pc}$ мкс, $l_2={2*pc}$ мкс. Дополнительно исследуется экспоненциальная КФ.
БГШ $X\sim N(0,2^2)$ → БПФ → умножение на $H=\sqrt{{\mathrm{{DFT}}(R)}}$ → ОБПФ → Y.
По Винеру — Хинчину $S_Y=|H|^2S_X$. Нормировка $R(0)=1$ сохраняет дисперсию; линейная фильтрация сохраняет гауссовость.
СКО 2 принято по номеру группы, поскольку отдельного значения в ЛР2 нет. Усредняются 10 КФ и 20 СПМ. Фильтрация циклическая; длительность записи значительно больше l.
''' + (r'Для треугольной КФ $S(f)=\sigma^2l\,\mathrm{sinc}^2(fl)$, где sinc нормированная.' if triangular else r'Для осциллирующей КФ СПМ имеет два гауссовских максимума на $\pm10/(2\pi l)$.')),('c',f'''dt=.05; count=32768; sigma=group; l1=pc
T=count*dt; t=np.arange(count)*dt; freq=np.fft.rfftfreq(count,dt)
tau=(np.arange(count)-count//2)*dt
x=rng.normal(0,sigma,(20,count))
def target(tau,l): return {expr}
def acf(a):
    a=a-a.mean(axis=-1,keepdims=True)
    c=signal.correlate(a,a,mode='full',method='fft')[len(a)-1:]
    return c/(len(a)*np.var(a))
def psd(a):
    p=np.abs(np.fft.rfft(a,axis=-1))**2*dt/count
    p[:,1:-1]*=2
    return p.mean(axis=0)
def shaped(fun):
    s=np.fft.rfft(np.fft.ifftshift(fun(tau))).real
    assert s.min()>-1e-7, 'КФ не положительно определена на выбранной сетке'
    s=np.maximum(s,0)
    y=np.fft.irfft(np.fft.rfft(x,axis=-1)*np.sqrt(s),n=count,axis=-1)
    theory=s*sigma**2*dt; theory[1:-1]*=2
    return y,theory
results={{'БГШ':(x,None,None)}}
for label,fun in [('Экспоненциальная',lambda q:np.exp(-np.abs(q)/l1)),
                  ('Вариант l₁',lambda q:target(q,l1)),('Вариант 2l₁',lambda q:target(q,2*l1))]:
    y,s=shaped(fun); results[label]=(y,s,fun)
    print(label,'M=',y.mean(),'D=',y.var(),'теория D=',sigma**2)
fig,axs=plt.subplots(2,2,figsize=(14,8))
for label,(y,s,fun) in results.items():
    axs[0,0].plot(t[:2000],y[0,:2000],lw=.7,label=label)
    axs[0,1].hist(y.ravel(),bins=80,density=True,histtype='step',label=label)
    axs[1,0].plot(np.arange(1000)*dt,np.mean([acf(a)[:1000] for a in y[:10]],axis=0),label=label)
    axs[1,1].plot(freq,psd(y),label=label)
g=np.linspace(-9,9,300); axs[0,1].plot(g,stats.norm.pdf(g,scale=sigma),'k--',label='N(0,σ²)')
for ax,title,xlab,ylab in zip(axs.flat,['Реализации','Распределения','КФ (10 реализаций)','СПМ (20 реализаций)'],['t, мкс','x','τ, мкс','f, МГц'],['x(t)','p(x)','R(τ)','S, ед.²/МГц']):
    ax.set(title=title,xlabel=xlab,ylabel=ylab); ax.legend(fontsize=8)
axs[1,1].set_xlim(0,2); plt.tight_layout(); plt.show()
fig,axs=plt.subplots(1,2,figsize=(14,5))
for label in ['Вариант l₁','Вариант 2l₁']:
    y,s,fun=results[label]; lag=np.arange(count)*dt; limit=lag<=6*l1
    line,=axs[0].plot(lag[limit],np.mean([acf(a)[limit] for a in y[:10]],axis=0),label=label+' оценка')
    axs[0].plot(lag[limit],fun(lag[limit]),'--',color=line.get_color(),label=label+' теория')
    line,=axs[1].plot(freq,psd(y),label=label+' оценка')
    axs[1].plot(freq,s,'--',color=line.get_color(),label=label+' теория')
axs[0].set(xlabel='τ, мкс',ylabel='R(τ)',title='Оценки и целевые КФ'); axs[1].set(xlabel='f, МГц',ylabel='S, ед.²/МГц',xlim=(0,2),title='СПМ: оценка и теория')
for ax in axs: ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
print('Интеграл СПМ / дисперсия:',np.sum(psd(results['Вариант l₁'][0]))/(count*dt),results['Вариант l₁'][0].var())
'''),('m',r'''## Выводы
Формирующий фильтр меняет корреляцию соседних отсчётов, сохраняя гауссовское распределение и ансамблевую дисперсию. При удвоении l КФ растягивается вдвое, а СПМ сжимается по частоте, сохраняя площадь. Усреднение уменьшает разброс оценок; смещённая оценка КФ содержит множитель $1-|\tau|/T$, поэтому при больших лагах отличается от цели.
Здесь оценивается центрированная нормированная ковариация. Для нулевого среднего она совпадает с нормированной корреляцией. При среднем m нецентрированная корреляция равна $B(\tau)=\sigma^2R(\tau)+m^2$, а ковариация — $K(\tau)=\sigma^2R(\tau)$.
Треугольная КФ имеет конечную область корреляции; осциллирующая КФ соответствует узкополосному шуму. Эти модели применяются к шумам после фильтра в радиоприёмнике.''')])
def lab3(num,pc):
    make(num,pc,3,[('m',r'''## Параметры сигнала и фильтров
$N=ПК+2$, $M=N\bmod10$, $L=N\bmod3$.
При L=0: видеоимпульс длительностью N нс; полосовой фильтр от $1/t_и$ до $2/t_и$.
При L=2: $x(t)=[1+0.5\cos(2\pi f_mt)]\cos(2\pi f_ct)$, $f_c=10N$ МГц, $f_m=\lfloor N/10\rfloor+M$ МГц; заградительный фильтр вырезает несущую.
Порядок прототипа n=4 и подавление Чебышёва II 40 дБ приняты, поскольку методичка их не задаёт. Итоговый порядок полосовых преобразований — 8. Для АМ ширина режекции выбрана $f_m/2$, чтобы сохранить боковые полосы.
Структура: **сигнал → БПФ → идеальная маска → ОБПФ**; параллельно **сигнал → SOS Баттерворта / SOS Чебышёва II**.
'''),('c','''N=pc+group; M=N%10; L=N%3
if L==0:
    ti=N*1e-9; fs=4e9; length=8192; t=np.arange(length)/fs
    start=200e-9; x=((t>=start)&(t<start+ti)).astype(float)
    edges=np.array([1/ti,2/ti]); btype='bandpass'; plotlim=(180,300); tscale=1e9; tunit='нс'
else:
    fc=10*N*1e6; fm=(N//10+M)*1e6; fs=1e9; length=8192; t=np.arange(length)/fs
    x=(1+.5*np.cos(2*np.pi*fm*t))*np.cos(2*np.pi*fc*t)
    edges=np.array([fc-fm/4,fc+fm/4]); btype='bandstop'; plotlim=(0,.8); tscale=1e6; tunit='мкс'
f=np.fft.rfftfreq(length,1/fs)
inside=(f>=edges[0])&(f<=edges[1]); mask=inside if L==0 else ~inside
ideal=np.fft.irfft(np.fft.rfft(x)*mask,n=length)
sos_b=signal.butter(4,edges,btype=btype,fs=fs,output='sos')
# Для Cheby2 Wn — границы полосы задерживания, а не точки −3 дБ.
sos_c=signal.cheby2(4,40,edges,btype=btype,fs=fs,output='sos')
yb=signal.sosfilt(sos_b,x); yc=signal.sosfilt(sos_c,x)
print(f'N={N}, M={M}, L={L}, частоты фильтра {edges/1e6} МГц')
print('Cheby2 задан по задерживанию −40 дБ; Butterworth — по уровню −3 дБ.')
fig,axs=plt.subplots(1,2,figsize=(14,4))
for name,y in [('Исходный',x),('Идеальный',ideal),('Баттерворт',yb),('Чебышёв II',yc)]:
    axs[0].plot(t*tscale,y,label=name,lw=1)
    amp=np.abs(np.fft.rfft(y))/length
    axs[1].plot(f/1e6,20*np.log10(np.maximum(amp,1e-10)),label=name)
axs[0].set(xlabel='t, '+tunit,ylabel='U',xlim=plotlim,title='Сигнал до и после фильтра')
axs[1].set(xlabel='f, МГц',ylabel='Амплитуда, дБ отн. 1',title='Спектры',xlim=((0,500) if L==0 else (fc/1e6-3*fm/1e6,fc/1e6+3*fm/1e6)),ylim=(-100,5))
for ax in axs: ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
w=np.linspace(0,fs/2,16000)
_,hb=signal.sosfreqz(sos_b,worN=w,fs=fs); _,hc=signal.sosfreqz(sos_c,worN=w,fs=fs)
passmask=(w>=edges[0])&(w<=edges[1]); hi=(passmask if L==0 else ~passmask).astype(float)
fig,axs=plt.subplots(1,2,figsize=(14,4))
for name,h in [('Идеальный',hi.astype(complex)),('Баттерворт',hb),('Чебышёв II',hc)]:
    axs[0].plot(w/1e6,20*np.log10(np.maximum(np.abs(h),1e-6)),label=name)
    ph=np.unwrap(np.angle(h)); ph[np.abs(h)<1e-5]=np.nan
    axs[1].plot(w/1e6,ph,label=name)
for ax in axs: ax.set(xlabel='f, МГц',xlim=((0,500) if L==0 else (fc/1e6-3*fm/1e6,fc/1e6+3*fm/1e6))); ax.legend()
axs[0].set(ylabel='|H|, дБ',ylim=(-100,5),title='АЧХ'); axs[1].set(ylabel='φ, рад',title='ФЧХ (при H=0 не определена)')
plt.tight_layout(); plt.show()
imp=np.zeros(length); imp[0]=1
h0=np.fft.fftshift(np.fft.irfft(mask.astype(float),n=length))
hb0=signal.sosfilt(sos_b,imp); hc0=signal.sosfilt(sos_c,imp)
fig,ax=plt.subplots()
ax.plot((np.arange(length)-length//2)/fs*tscale,h0,label='Идеальная, центрированная')
ax.plot(t*tscale,hb0,label='Баттерворт'); ax.plot(t*tscale,hc0,label='Чебышёв II')
ax.set(xlabel='t, '+tunit,ylabel='h(t)',title='Импульсные характеристики',xlim=((-80,160) if L==0 else (-.5,1.5))); ax.legend(); plt.show()
# Растекание спектра: целое и дробное число периодов, с окном и без.
n=np.arange(256); fig,ax=plt.subplots()
for k in [20,20.5]:
    for win,label in [(np.ones(256),'прямоугольное'),(np.hamming(256),'Хэмминг')]:
        a=np.abs(np.fft.rfft(np.cos(2*np.pi*k*n/256)*win))/win.sum()
        ax.plot(np.arange(len(a)),20*np.log10(np.maximum(a,1e-8)),label=f'k={k}, {label}')
ax.set(xlabel='Номер частотного отсчёта',ylabel='Амплитуда, дБ',xlim=(10,32),ylim=(-100,0),title='Растекание спектра'); ax.legend(); plt.show()
'''),('m',r'''## Выводы
Идеальная маска резко ограничивает спектр, но её ИХ двусторонняя и бесконечная: отклик до воздействия означает некаузальность. БПФ реализует циклическую свёртку на конечной записи, что требует осторожности с границами. БИХ-фильтры каузальны, имеют переходную полосу, нелинейную фазу и затухающую ИХ. В начале записи наблюдается переходный процесс.
Баттерворт имеет монотонную АЧХ, Чебышёв II — пульсации в полосе задерживания и нули передачи; одинаковые численные Wn у них задают разные уровни. На частотах нулей передачи фаза не определена.
Для видеоимпульса полосовая фильтрация подавляет постоянную составляющую и формирует колебательный отклик. Для АМ заградительный фильтр подавляет несущую, оставляя две боковые полосы. Окно Хэмминга уменьшает боковые лепестки при расширении главного; дробное число периодов даёт растекание спектра.''')])
def lab4(num,pc):
    make(num,pc,4,[('m',r'''## Нестационарный сигнал
$N=ПК+2$, $L=N\bmod3$. При L=0 формируем ЛЧМ от $(1000+20N)$ до $(1400+20N)$ кГц. Для ЛЧМ принято $t_и=40$ мкс: видеоимпульс N нс из ЛР3 короче одного периода мегагерцевой несущей и не позволяет показать перестройку. Это явное моделирующее допущение, унаследованное из выбранного ранее шаблона.
При L=2 формируем ППРЧ: пять каналов с шагом $3f_m$, длительность чипа $2/f_m$; несущая и частота модуляции взяты из ЛР3. Между чипами введены короткие паузы 4% длительности чипа для исследования временного разрешения.
Структура: **генератор частот → формирование фазы и огибающей → сигнал → STFT / CWT**.
Для STFT $\Delta f\approx f_s/N_w$, шаг $H=N_w-\mathrm{noverlap}$. Длинное окно улучшает частотное разрешение и размывает паузы; уменьшение шага делает временную сетку плотнее, но не улучшает собственное разрешение окна.
'''),('c','''N=pc+group; M=N%10; L=N%3
chips=8
if L==0:
    fs=8e6; ti=40e-6; gap=.04*ti; f0=(1000+20*N)*1e3; f1=(1400+20*N)*1e3
    unit=int(round(ti*fs)); pause=int(round(gap*fs)); x=np.zeros(chips*(unit+pause))
    local=np.arange(unit)/fs
    chip=np.cos(2*np.pi*(f0*local+(f1-f0)*local**2/(2*ti)))
    for j in range(chips): x[j*(unit+pause):j*(unit+pause)+unit]=chip
    short=8; long=80; flim=(.8,1.9)
    print('ЛЧМ:',f0/1e3,'→',f1/1e3,'кГц; tи=',ti*1e6,'мкс')
else:
    fc=10*N*1e6; fm=(N//10+M)*1e6; ti=2/fm; gap=.04*ti; fs=400e6
    channels=fc+np.arange(-2,3)*3*fm
    unit=int(round(ti*fs)); pause=int(round(gap*fs)); x=np.zeros(chips*(unit+pause))
    order=rng.permutation(5).tolist()+rng.integers(0,5,size=chips-5).tolist()
    local=np.arange(unit)/fs
    for j,k in enumerate(order):
        x[j*(unit+pause):j*(unit+pause)+unit]=np.cos(2*np.pi*channels[k]*local)
    short=8; long=128; flim=(0,100)
    print('Каналы, МГц:',channels/1e6,'порядок:',order,'длительность чипа, мкс:',ti*1e6)
t=np.arange(len(x))/fs
fig,ax=plt.subplots(); ax.plot(t*1e6,x,lw=.7); ax.set(xlabel='t, мкс',ylabel='U',title='Нестационарный сигнал'); plt.show()
print('Пауза:',pause,'отсчётов =',pause/fs*1e6,'мкс')
def spec(ax,window,nwin,hop,title):
    f,ts,p=signal.spectrogram(x,fs=fs,window=window,nperseg=nwin,noverlap=nwin-hop,nfft=max(1024,nwin),detrend=False,scaling='density',mode='psd')
    z=10*np.log10(np.maximum(p,1e-20))
    im=ax.pcolormesh(ts*1e6,f/1e6,z,shading='auto',vmin=z.max()-65,vmax=z.max())
    ax.set(xlabel='t, мкс',ylabel='f, МГц',ylim=flim,title=title)
    plt.colorbar(im,ax=ax,label='СПМ, дБ/Гц')
    return len(ts)
fig,axs=plt.subplots(1,2,figsize=(14,4))
for ax,win in zip(axs,['boxcar','hamming']):
    spec(ax,win,long,1,f'{win}: окно {long}, шаг 1')
plt.tight_layout(); plt.show()
fig,axs=plt.subplots(1,3,figsize=(18,4))
spec(axs[0],'hamming',short,1,f'Короткое окно {short}: паузы')
columns1=spec(axs[1],'hamming',long,1,f'Окно {long}, шаг 1')
columns2=spec(axs[2],'hamming',long,long,f'Окно {long}, шаг {long}')
plt.tight_layout(); plt.show()
print('Количество временных окон: шаг 1 / шаг Nw:',columns1,columns2)
# Непрерывное вейвлет-преобразование, физическая ось частот.
wavelet='cmor1.5-1.0'
freqs=np.linspace(max(flim[0],.1),flim[1],180)*1e6
scales=pywt.central_frequency(wavelet)*fs/freqs
coef,fw=pywt.cwt(x,scales,wavelet,sampling_period=1/fs,method='fft')
power=np.abs(coef)**2
fig,ax=plt.subplots(figsize=(13,5))
z=10*np.log10(np.maximum(power,1e-15))
im=ax.pcolormesh(t*1e6,fw/1e6,z,shading='auto',vmin=z.max()-45,vmax=z.max())
ax.set(xlabel='t, мкс',ylabel='f, МГц',title='CWT: комплексный вейвлет Морле (не калиброванная СПМ)')
plt.colorbar(im,ax=ax,label='|CWT|², дБ отн. 1'); plt.tight_layout(); plt.show()
assert np.all(np.isfinite(coef))
'''),('m',r'''## Выводы
Прямоугольное окно даёт узкий главный лепесток, но сильнее растекается по частоте. Хэмминг подавляет боковые лепестки, расширяя основной. Короткое окно выделяет паузы, но размывает частоты; длинное лучше разделяет каналы или показывает наклон ЛЧМ, зато сглаживает моменты переключения. Шаг 1 даёт более плотную картину, а шаг в окно — меньше временных столбцов при том же частотном разрешении. Нулевое дополнение БПФ интерполирует спектр и не заменяет увеличение окна.
CWT меняет временное разрешение с частотой: на высоких частотах эффективное окно короче. Края записи подвержены краевым эффектам, поэтому яркость у границ не следует интерпретировать как отдельные сигналы. Значения |CWT|² не равны калиброванной СПМ STFT.''')])

def transient_cells():
    return [('m',r"""## КИХ через FFT и БИХ: включение, прохождение и выключение сигнала

Идеальная частотная маска выше имеет бесконечную двустороннюю ИХ. Для реализуемого **КИХ** задаём конечную ИХ оконным методом `firwin` и вычисляем **линейную свёртку через FFT** (`fftconvolve`, с нулевым дополнением). КИХ каузален, имеет линейную фазу и задержку $(K-1)/(2f_s)$.

Три фильтра: КИХ–FFT, БИХ Баттерворта и БИХ Чебышёва II. Начальные состояния нулевые. Вход содержит три участка: тишина, сигнал, тишина после сигнала. Для видеоимпульса сохраняется длительность по варианту. Для АМ несущая включается на конечный интервал; параметры АМ сохраняются.

Измеряем максимум выхода, отношение энергий выхода и входа, момент максимума, энергию остаточного отклика после выключения и время, после которого |y| остаётся ниже 1% максимума выхода. Последний показатель — длительность затухания по выбранному порогу, а не точное время исчезновения БИХ-отклика. БИХ теоретически затухает бесконечно. Для полосового сигнала задержка зависит от частоты; разность положений пиков не является универсальной групповой задержкой.
"""),('c',r"""
# Конечный КИХ: те же границы частот и тот же тип фильтра.
numtaps=1025 if L==0 else 2049
fir=signal.firwin(numtaps,edges,pass_zero=(L!=0),window='hamming',fs=fs)
fir_delay=(numtaps-1)/(2*fs)
if L==0:
    on=200e-9; duration=ti; total=2e-6
else:
    on=1e-6; duration=2e-6; total=16e-6
ns=int(round(total*fs)); tt=np.arange(ns)/fs
start_index=int(round(on*fs)); active_count=int(round(duration*fs))
end_index=start_index+active_count; off=end_index/fs
xx=np.zeros(ns)
local=np.arange(active_count)/fs
xx[start_index:end_index]=(np.ones(active_count) if L==0 else
    (1+.5*np.cos(2*np.pi*fm*local))*np.cos(2*np.pi*fc*local))
outputs={
    'КИХ через FFT':signal.fftconvolve(xx,fir,mode='full')[:ns],
    'БИХ Баттерворта':signal.sosfilt(sos_b,xx),
    'БИХ Чебышёва II':signal.sosfilt(sos_c,xx)}
assert np.allclose(outputs['КИХ через FFT'],signal.lfilter(fir,[1],xx),atol=1e-11)
assert all(np.max(np.abs(y[:start_index]))<1e-10 for y in outputs.values())
print(f'КИХ: {numtaps} коэффициентов, порядок {numtaps-1}, задержка {fir_delay*tscale:.3f} {tunit}')
# Общий вход и выход каждого фильтра: тишина → воздействие → хвост.
fig,axs=plt.subplots(3,1,figsize=(14,10),sharex=True)
for ax,(name,y) in zip(axs,outputs.items()):
    ax.axvspan(0,on*tscale,color='gray',alpha=.12,label='До сигнала: вход 0')
    ax.axvspan(on*tscale,off*tscale,color='green',alpha=.08,label='Сигнал на входе')
    ax.axvspan(off*tscale,total*tscale,color='orange',alpha=.10,label='После выключения: вход 0')
    ax.plot(tt*tscale,xx,color='gray',alpha=.6,lw=.7,label='Вход')
    ax.plot(tt*tscale,y,lw=.9,label='Выход')
    ax.axvline(on*tscale,color='green',ls='--'); ax.axvline(off*tscale,color='red',ls='--')
    ax.set(title=name,ylabel='U'); ax.legend(fontsize=8,loc='upper right')
axs[-1].set(xlabel='t, '+tunit,xlim=(0,total*tscale))
plt.tight_layout(); plt.show()
# Увеличение трёх этапов: одинаковые оси у всех фильтров.
before_width=40e-9 if L==0 else .2e-6
post_width=400e-9 if L==0 else 3e-6
ranges=[(on-before_width,on),(on,off),(off,off+post_width)]
fig,axs=plt.subplots(1,3,figsize=(18,4))
for ax,(a,b),title in zip(axs,ranges,['Сигнала ещё нет','Сигнал действует','Вход выключен: остаточный отклик']):
    sel=(tt>=a)&(tt<=b)
    ax.plot(tt[sel]*tscale,xx[sel],'k:',label='Вход',alpha=.7)
    for name,y in outputs.items(): ax.plot(tt[sel]*tscale,y[sel],label=name,lw=1)
    ax.set(title=title,xlabel='t, '+tunit,ylabel='U'); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
# Количественная оценка прохождения и затухания.
Ein=np.sum(xx**2)
print('Фильтр | max|y| | Eвыход/Eвход | t максимума | хвост/Eвыход | затухание после выключения (1%)')
for name,y in outputs.items():
    peak=np.max(np.abs(y)); energy=np.sum(y**2)
    above=np.flatnonzero(np.abs(y[end_index:])>peak*.01)
    decay=((above[-1]+1)/fs) if len(above) else 0.
    settled=not len(above) or above[-1]<len(y[end_index:])-1
    decay_text=f'{decay*tscale:.3f} {tunit}' if settled else 'не затух за запись'
    print(f'{name} | {peak:.5f} | {energy/Ein:.5f} | {tt[np.argmax(np.abs(y))]*tscale:.3f} {tunit} | '
          f'{np.sum(y[end_index:]**2)/energy:.5f} | {decay_text}')
# АЧХ, ФЧХ и ИХ именно реализуемых трёх фильтров.
ff=np.linspace(0,fs/2,24000)
_,hf=signal.freqz(fir,worN=ff,fs=fs)
_,hb=signal.sosfreqz(sos_b,worN=ff,fs=fs)
_,hc=signal.sosfreqz(sos_c,worN=ff,fs=fs)
fig,axs=plt.subplots(1,3,figsize=(18,4))
for name,h in [('КИХ через FFT',hf),('БИХ Баттерворта',hb),('БИХ Чебышёва II',hc)]:
    axs[0].plot(ff/1e6,20*np.log10(np.maximum(np.abs(h),1e-8)),label=name)
    ph=np.unwrap(np.angle(h)); ph[np.abs(h)<1e-4]=np.nan
    axs[1].plot(ff/1e6,ph,label=name)
probe=np.zeros(ns); probe[0]=1
for name,h in [('КИХ через FFT',np.pad(fir,(0,ns-len(fir)))),
               ('БИХ Баттерворта',signal.sosfilt(sos_b,probe)),
               ('БИХ Чебышёва II',signal.sosfilt(sos_c,probe))]:
    axs[2].plot(tt*tscale,h,label=name)
flim=(0,300) if L==0 else (fc/1e6-3*fm/1e6,fc/1e6+3*fm/1e6)
axs[0].set(title='АЧХ трёх фильтров',xlabel='f, МГц',ylabel='|H|, дБ',xlim=flim,ylim=(-100,5))
axs[1].set(title='ФЧХ трёх фильтров',xlabel='f, МГц',ylabel='φ, рад',xlim=flim)
axs[2].set(title='Каузальные импульсные характеристики',xlabel='t, '+tunit,ylabel='h(t)',xlim=(0,(.5e-6 if L==0 else 4e-6)*tscale))
for ax in axs: ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
"""),('m',r"""### Интерпретация переходных процессов
При нулевом входе и нулевых начальных состояниях все три выхода равны нулю (малые значения FFT порядка машинной точности не являются физическим откликом). После включения возникает переходный процесс. КИХ задерживает сигнал на известное число отсчётов; его импульсный отклик конечен. БИХ накапливают состояние в обратных связях, поэтому после выключения входа остаётся затухающий колебательный хвост.

Таблица показывает, какая доля энергии прошла через фильтр и какая её часть вышла уже после выключения входа. Отношение энергий относится ко всему импульсу; оно не является коэффициентом передачи на одной частоте. У заградительного фильтра АМ несущая подавляется, но боковые полосы проходят. Конечная длительность входа дополнительно расширяет спектр и возбуждает переходные процессы на границах.
""")]

if __name__=='__main__':
    for num,pc in [(10,10),(3,3)]:
        lab1(num,pc); lab2(num,pc); lab3(num,pc); lab4(num,pc)
        print('Создан комплект',num,pc)
