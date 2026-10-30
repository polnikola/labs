f_hz = 1e6;
omg = f_hz*1*pi;

t_d = 1.5e-6;
f_d = 1/t_d;
t_sample = 1/f_hz*1e3-t_d;
t_axis = 0:t_d:t_sample;

signal = sin(omg*t_axis);
spectr = fft(signal);
f_axis = 0:1/t_sample:f_d;
figure()
subplot(2,1,1)
plot(t_axis,signal)
subplot(2,1,2)
plot(f_axis,abs(spectr))

%% Gh
f_hz = 0;         % циклическая частота, Гц
omg = f_hz*2*pi;    % радиальная частота

t_d = 1/8;         % период дискретизации, с
f_d = 1/t_d;        % частота дискретизации
t_sample = 8*t_d-t_d;  % длина окна
t_axis = 0:t_d:t_sample;    % ось времени

signal = cos(omg*t_axis);
spectr = fft(signal)/length(signal);
f_axis = 0:1/(t_sample+t_d):f_d-1/(t_sample+t_d);
figure('Name','Сп. инт. сигн.', 'WindowStyle','docked', 'Color','white')
subplot(2,1,1)
plot(t_axis,signal,':*')
title('Signal');
subplot(2,1,2)
plot(f_axis,abs(spectr),':*')
title('Spectre'); ylim([-1, 1]);
% subplot(2,2,3)
% plot(f_axis,real(spectr),':*')
% title('re'); ylim([-1, 1]);
% subplot(2,2,4)
% plot(f_axis,imag(spectr),':*')
% title('im'); ylim([-1, 1]);


disp('done')

%% Соответствие между сигналами и спектрами 1
% Соответствие между "чистыми" частотами

% Настройки частотного и временного пространства
f_d = 8;                % частота дискретизации
t_d = 1/f_d;            % период дискретизации, с
n_sample = 8;
t_sample = n_sample*t_d-t_d;   % длина окна (целое число интервалов дискретизации)
t_axis = 0:t_d:t_sample;                            % ось времени
f_axis = 0:1/(t_sample+t_d):f_d-1/(t_sample+t_d);   % ось частот
fft_axis_labels = [f_axis(1: floor(end/2)+1), f_axis(floor(end/2):-1:2)] ;
% filter_f_char(end-(mod(n_signal,2)==0):-1:2)

figure('Name','Сп. инт. сигн.', 'WindowStyle','docked', 'Color','white')
for i=1:5
    f_hz = f_axis(i);   % циклическая частота сигнала, Гц
    omg = f_hz*2*pi;    % радиальная частота сигнала, рад/с
    signal = cos(omg*t_axis);   % формирование сигнала
    spectr = fft(signal)/length(signal);

    subplot(5,2,2*i-1)
    plot(t_axis,signal,':x')
    title(num2str(f_hz,'Сигнал %d Гц')); ylim([-1.5, 1.5]);

    subplot(5,2,2*i); hold on;
    plot(f_axis,abs(spectr),':*')
    plot(f_axis,real(spectr),':*')
    plot(f_axis,imag(spectr),':*')
    xticklabels(fft_axis_labels)
    title(num2str(f_hz,'Спектр %d Гц')); ylim([-1, 1]);

end

%% Спектр сигнала, не попадающего на множители частот