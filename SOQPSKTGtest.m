% This code follows this paper [1]:
%
%  https://kuscholarworks.ku.edu/bitstream/handle/1808/7644/ReaZanabria
%  _ku_0099M_11339_DATA_1.pdf;jsessionid=40B15F86A45CC95AC23467A07A278C
%  50?sequence=1
%________________________________________________________________________
% For now, phi(t;alpha) is taken from this paper [2]:
%
% https://apps.dtic.mil/dtic/tr/fulltext/u2/a620053.pdf
%________________________________________________________________________
% Additional reference [3], final graph looks similar to one shown here:
%
% https://dsp.stackexchange.com/questions/55791/soqpsk-tg-pulse-shaping
%________________________________________________________________________

clc; clear; close all;

global p; global A; global B; global T1;
global T2; global L; global h; global T;
global E;

% Parameters specific to SOQPSK-TG
p = 0.7; A = 0.3112; B = 1.25; T1= 1.5;
T2 = 0.5; L = 8; h = 0.5; T = 1;
E = 1;

% Random bitstream generation
number_of_bits = 100;
u = randi([0 1],[1,number_of_bits]);
%u = zeros(1,100);
%u(1) = 1;
%u(2) = 1;

% Convert bitstream to a ternary sequence 
% using the standard precorder (Equ 2.8)
alpha = standard_precorder(u);

% Implement the window function
% unique to the TG vairant of SOQPSK (Equ 2.5)
% -- On line 160


% Implement the partial-resposne frequency pulse
% unique to the TG vairant of SOQPSK (Equ 2.5)
% Functions used:
% - window function

global fTG;
fTG = @(t)((A.*cos(pi.*p.*((B.*t)./(2.*T))))./(1 - (4.*((p.*((B.*t)./(2.*T))).^2))))...
      .* (sin(pi.*((B*t)./(2.*T)))./(pi.*((B.*t)./(2.*T)))) .* w(t);

% According to [3] and by extension [1], 
% fTG must be shifted by L*T/2 in order to get
% a smooth transitions between bits
% Frequency pulse centered at y = 0 is now centered at y = 4
global fTGs;
fTGs = @(t) fTG(t - L*T/2);  

% Precompute fTGs values for fasttrapezoids()
global xfTGs; global savedfTGs; global accuracy;
accuracy = 1000;
xfTGs = 0:1/accuracy:8;
savedfTGs = zeros(length(xfTGs),1);
for i = 1:length(xfTGs)
    savedfTGs(i) = fTGs(xfTGs(i));
end
savedfTGs(4*accuracy + 1) = 0.3112;

% Precompute integral of fTGs values for fastintegral()
global saveInt; global intaccuracy;
intaccuracy = 10000;
saveInt = getfield(load('saveInt10000.mat'), 'saveInt');
saveInt(length(saveInt)) = saveInt(length(saveInt)-1);
saveInt(4*intaccuracy + 1) = 0.25;

% Implement a function for the phase pulse q(t) ([1], Equ 2.3)
% -- On line 173
% Functions used:
% - partial-resposne frequency pulse
%   - window function


% Implement phase fuction phi(t;alpha) ([1], Equ 2.4*)
% * Currently using Equ 2.2 instead
% -- On line 241
% Functions used:
% - phase pulse fucntion
%   - partial-resposne frequency pulse
%     - window function


% Implement signal function s(t;alpha) ([1], Equ 2.1)
% -- On line 278
% Functions used:
% - phase function
%   - phase pulse fucntion
%     - partial-resposne frequency pulse
%       - window function

%% Graph the Frequency and Phase Pulses
% Refer to figure 2.1 in [1] 
figure('Name','Frequency and Phase Pulse', 'Position', [100 100 1000 500]);
plotter(fTGs, 0, 8, 0.1);
hold on
xw = 0:0.01:8;
yw = zeros(length(xw),1);
for i = 1:length(xw)
    yw(i) = q(xw(i));
end
plot(xw,yw,'LineStyle','--');
hold off
ylim([-0.2,0.6])
xlabel('Normalized Time (t/T)');
ylabel('Amplitude');
legend('fTG(t), frequency pulse', 'qTG(t), phase pulse', ...
       'Location','northwest');
title('Frequency pulse and phase pulse for SOQPSK-TG');

%% Graph the Phase Function
figure('Name','Phase Function', 'Position', [100 100 1000 500]);
xw = 0:0.1:length(alpha);
yw = zeros(length(xw),1);
for i = 1:length(xw)
    yw(i) = phi(xw(i),alpha);
end
plot(xw,yw)
hold on
%xa = 1:length(alpha);
%plot(xa, alpha)
%plot(xa, u)
hold off
grid on
title('Phase function');
legend('phi(t;alpha)','Location','northwest');

%% Graph the Binary, Ternary, and SOQPSK-TG representaions 
% of the original bitstream
figure('Name','Wave Representations','Position', [100 100 1000 500]);
xw = 0:0.1:length(alpha)*1.1;
yw = zeros(length(xw),1);
for i = 1:length(xw)
    yw(i) = s(xw(i),alpha);
end
plot(xw,real(yw))
hold on
xa = 1:length(alpha);
stairs(alpha + 2.5);
stairs(u + 4);
hold off
grid on
title('Binary, Ternary and Modulated wave representations');
xlim([0,length(alpha)*1.1]);
xticks(floor(linspace(0,length(alpha)*1.1,13)));
ylim([-1.25,5.25])
yticks([-1 -0.5 0 0.5 1 1.5 2.5 3.5 4 5]);
yticklabels({'-1','0.5','0','0.5','1','-1','0','1','0','1'})
legend('Real Part of Output Wave', 'Ternary Data', 'Binary Data', 'Location', 'southoutside');

%% Implement true OQPSK functionality by splittng output wave
% into real and imaginary (I and Q) components, time shifting
% the Q wave by half the symbol length, and summing the reuslt.
figure('Name','Wave Representations','Position', [100 100 1000 500]);
plot(xw,real(yw) + 5)
hold on
plot(xw + T/2,imag(yw) + 2.5)
size = length(yw);
spacing = xw(2) - xw(1);
yw_offset = uint32((14.9-7.8)/2)/spacing;
wave = zeros(1,length(yw) - yw_offset);
for i = 1:length(yw) + yw_offset
    if not(or(i > size, i - yw_offset < 1))
        wave(i) = real(yw(i)) + imag(yw(i - yw_offset));
    end
end
plot(xw(yw_offset+1:length(wave)),wave(yw_offset+1:length(wave))./2)
legend('Real Part', 'Imaginary Part', 'SOQPSK-TG Wave', 'Location', 'southoutside');
grid on 
title('Real and Imaginary Parts of signal wave');
xlim([0,length(alpha)*1.1]);
xticks(floor(linspace(0,length(alpha)*1.2,13)));
ylim([-1.25,6.25])
yticks([-1 -0.5 0 0.5 1 1.5 2 2.5 3 3.5 4 4.5 5 5.5 6]);
yticklabels({'-1','0.5','0','0.5','1','-1','0.5','0','0.5','1','-1','0.5','0','0.5','1'})

%% Eye Diagram
[xValues, signal] = SOQPSKTGMod(u);
eyediagram(signal,40)
eye_diagram(signal, 10, 40, 'Real')

%% graph real RF
sps = 20;  % samples per symbol
xw = linspace(0, length(alpha)-1, length(alpha)*sps);  % samples
yw = zeros(length(xw),1);  % complex baseband signal
for i = 1:length(xw)
    yw(i) = s(xw(i),alpha);
end
I = real(yw);
Q = imag(yw);

fs = 48e6;
fc = 2.4e6;  % carrier signal frequency
t = (0:1/fs:(length(yw)-1)/fs)';
Iup = I.*cos(fc*2*pi*t);  % multiply I by carrier signal
Qup = -Q.*sin(fc*2*pi*t);  % multiply Q by carrier offset 90deg
S = Iup + Qup;  % real RF signal
IQup = yw.*exp(1i*2*pi*fc*t);
S1 = real(IQup);

% plot frequency spectrum
%fftS = fftshift(fft(IQup));
%f = fs/2*linspace(-1,1,length(t));
figure()
%plot(f, abs(fftS))
freqz(IQup, 1, 2^18, 'whole', fs)

% plot I and upsampled I
figure('Name', 'I and Iup')
plot(xw, I)
hold on
plot(xw, Iup)
hold off
title('I and Iup')
xlabel('symbols, t/Ts')
legend('I','Iup','Location','southoutside')

%plot Q and upsampled Q
figure('Name', 'Q and Qup')
plot(xw, Q)
hold on
plot(xw, Qup)
hold off
title('Q and Qup')
xlabel('symbol, t/Ts')
legend('Q','Qup','Location','southoutside')

%plot Iup + Qup
figure('Name', 'Real RF Wave')
plot(t, S)
title('Real RF Wave')
xlabel('t (sec)')


%% Standard precorder function
function alpha = standard_precorder(bitstream)
    number_of_bits = length(bitstream);
    tempalpha = zeros(1,number_of_bits);
    for k = 3:number_of_bits
        tempalpha(k) = ((-1)^(k+1))*(2*bitstream(k-1) - 1)*(bitstream(k) - bitstream(k-2));
    end
    alpha = zeros(1,2*number_of_bits);
    for k = 1:number_of_bits
        alpha((2*k)-1) = tempalpha(k);
    end
end

%% Window Function
function window = w(t)
    global T1; global T2; global T;
    check = abs(t/(2*T));
    if and(0 <= check, check < T1)
        window = 1;
    elseif (T1 + T2) < check
        window = 0;
    else
        window = 0.5 + 0.5*cos((pi/T2)*((t/(2*T)) - T1));
    end
end

%% Phase pulse function
function phase = q(t)
    global L; global T; %global fTGs;
    if t <= 0
        phase = 0;
    elseif t >= L*T
        phase = 0.5;
    else
        % phase = integral(fTG,0,t);
        % phase = trapezoids(fTGs,0,t,500);
        % phase = fasttrapezoids(t);
        phase = fastintegral(t);
    end
    
    % Small fix, was seeing a couple of unexplainable 0.02 wide holes
    % at points like 6.2 and 6.4 in graph, suspect issue in trapezoids()
    % Can remove these lines, will have very small effect
    % EDIT - no longer using trapezoids, lines commented out
    
    %if isnan(phase)
        %phase = (q(t-0.02) + q(t + 0.02))/2;
    %end
end

%% Trapezoid rule integration
% MATLAB's Integral function bugs when integrating fTG
% Old integral function was giving issues at
% x > 3 and x < -3 in non-shifted frequency graph,
% did not like multiplying fTG by w(t)
function int = trapezoids(f,a,b,n)
    h = (b-a)/n;
    int = 0;
    for k = 1:(n-1)
         int = int + feval(f,a + h*k);
    end
    fa = f(a);
    if isnan(fa)
        fa = f(a + 0.0001);
    end
    int = (h.*(fa + f(b))./2) + h.*int;
end

%% Fast trapezoids
% Trapezoid rule implemented above is incredibly slow and inefficient
% This function takes advantage of precomputed values for fTGs
% and uses the inbuilt trapz() function
function int = fasttrapezoids(b)
    global savedfTGs; global accuracy; global xfTGs;
    offset = b*accuracy + 1;
    if offset > length(savedfTGs)
        offset = length(savedfTGs);
    end
    int = trapz(xfTGs(1:offset), savedfTGs(1:offset), 1);
end

%% Fast Integral
% If fTGs values can be precomputed, why not precomute the integral?
% 80000 points were taken over a range of 0-8, the only range that
% matters thanks to the window function (fGTs is zero everywhere else)
function int = fastintegral(b)
    global saveInt; global intaccuracy;
    offset = floor(b*intaccuracy + 1);
    if offset > length(saveInt)
        offset = length(saveInt);
    end
    int = saveInt(offset);
end

%% phi(t;alpha)
function phase = phi(t, alpha)
    % [1]'s implementation - k was never explained as a variable
    %{
        global L; global T; global h;

        % theta(t;ck;alphak)
        sum = 0; k = length(alpha); % wtf is k???
        for i = (k-L):(k)    % Matlab indicies start at 1, offset is needed
            sum = sum + alpha(i) * q(t - i*T);
        end
        sum = sum*2*pi*h;

        %thetak
        sum2 = 0;
        for i = 1:(k-L)   % Matlab indicies start at 1, offset is needed
            sum2 = sum2 + alpha(i);
        end
        sum2 = sum2 * pi * h;

        %phi(t;alpha)
        phase = sum + sum2;
    %}
    
    % [2]'s implementation - looks like it works, no way to verify unless
    % SOQPSK-TG demodulator is implemented
    global T; global h;
    t = t - 4;
    sum = 0;
    % Matlab indicies start at 1, offset is needed
    for i = 1:length(alpha)-1    
        sum = sum + alpha(i) * q(t - (i)*T);
    end
    phase = sum*2*pi*h;
    
end

%% SOQPSK-TG signal baseband representation
function signal = s(t, alpha)
    global E; global T;
    signal = sqrt(E/T) * exp(1i*phi(t, alpha));
end

%% SOQPSK-TG signal baseband representation with OQPSK-style modulation
function [xValues, signal] = real_signal(alpha)
    xValues = 1:0.1:length(alpha);
    nonmod = zeros(length(xValues),1);
    for i = 1:length(xValues)
        nonmod(i) = s(xValues(i),alpha);
    end
    size = length(nonmod);
    spacing = xValues(2) - xValues(1);
    % div by spacing to make indexes line up with values
    yw_offset = uint32(14.9-7.8)/spacing;  %- with this spacing
    signal = zeros(1,(size - yw_offset));
    for i = 1:length(nonmod) + yw_offset
        if not(or(i > size, i - yw_offset < 1))
            signal(i) = real(nonmod(i)) + 1i*imag(nonmod(i - yw_offset));
        end
    end
    xValues = xValues(yw_offset+1:length(signal));
    signal = signal(yw_offset+1:length(signal));
end

%% End-to-end function for modulation of the bitstream in SOQPSK-TG
% bitstream is vector with values in [0 1]
function [xValues, signal] = SOQPSKTGMod(bitstream)
    alpha = standard_precorder(bitstream);
    [xValues, signal] = real_signal(alpha);
end

%% End-to-end function for modulation of the bitstream in SOQPSK-TG
% bitstream is vector with values in [0 1]
function [xValues, signal] = SOQPSKTGNonMod(bitstream)
    alpha = standard_precorder(bitstream);
    xValues = 0:0.1:length(alpha);
    signal = zeros(length(xValues),1);
    for i = 1:length(xValues)
        signal(i) = s(xValues(i),alpha);
    end
end

%% Eye diagram plotter, use as an alternative to eyediagram()
function eye_diagram(signal, bits_per_symbol, n, name)
    figure('Name', append(name,' Eye Diagram'), 'Position', [100 100 500 500]);
    %title('Imag Eye Diagram');
    subplot(2,1,1);
    title('Eye Diagram for In-Phase Signal (I)');
    hold on;
    signal_graph = real(signal);
    spacing = 2*bits_per_symbol;
    for i=1:(length(signal_graph)/spacing)-n
        offset = i*spacing - spacing  + 1; 
        plot(0:n, signal_graph(offset:offset+n)); 
    end
    hold off;
    xlabel('Time');
    ylabel('Amplitude');
    xticks([0, floor(n/2), n]);
    xticklabels({'-0.5','0','0.5'})
    subplot(2,1,2);
    hold on;
    signal_graph = imag(signal);
    spacing = 2*bits_per_symbol;
    for i=1:(length(signal_graph)/spacing)-n
        offset = i*spacing - spacing  + 1; 
        plot(0:n, signal_graph(offset:offset+n)); 
    end
    title('Eye Diagram for Quadrature Signal (Q)');
    hold off;
    xlabel('Time');
    ylabel('Amplitude');
    xticks([0, floor(n/2), n]);
    xticklabels({'-0.5','0','0.5'})
end

%% Helps when plotting functions
function plotter(func, lower, upper, step)
    xw = lower:step:upper;
    yw = zeros(length(xw),1);
    for i = 1:length(xw)
        yw(i) = func(xw(i));
    end
    plot(xw,yw);
end
