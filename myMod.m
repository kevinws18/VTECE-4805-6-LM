clear
clc

% This one doesn't use the built in MATLAB function
% I think its just as effective and hopefully easier to follow
% Currently follows OQPSK modulation scheme
% TODO: shape it (whatever that means)

% create random 2-bit symbols
num_symbols = 10;
symbols = randi([0 3],num_symbols,1);

% initialize I, Q, and output signal
I = zeros(1,num_symbols*2+1);
Q = zeros(1,num_symbols*2+1);
fs = 1000; % sampling frequency? how many points I plot per phase-shift
OQPSK_signal = zeros(1,fs*(2*num_symbols));

% Here is the mapping I used: 45, 135, 225, 315 degrees
%       Q
%   01  |  00
%  _____|_____I
%       |
%   11  |  10

% Q is delayed by half a period (period is one symbol) to prevent jumps
% greater than 90deg
% I changes at start of period and Q changes halfway
% through (so there will be two phase shifts per symbol)
% This is the O (offset) part of OQPSK
% Example:
%    00 01 11 00 10
% I: ++|--|--|++|++
% Q:  +|++|+-|-+|+-

% map each symbol to point on I/Q axis
for i = 1:num_symbols
    if symbols(i) == 0
        I(2*i-1) = 1; % I(1, 3, 5,...)  I changes at beginning of period
        I(2*i) = 1;   % I(2, 4, 6,...)  and stays there
        Q(2*i) = 1;   % Q(2, 4, 6,...)  Q changes halfway through
        Q(2*i+1) = 1; % Q(3, 5, 7,...)  and stays there
    elseif symbols(i) == 1
        I(2*i-1) = -1;
        I(2*i) = -1;
        Q(2*i) = 1;
        Q(2*i+1) = 1;
    elseif symbols(i) == 2
        I(2*i-1) = 1;
        I(2*i) = 1;
        Q(2*i) = -1;
        Q(2*i+1) = -1;
    elseif symbols(i) == 3
        I(2*i-1) = -1;
        I(2*i) = -1;
        Q(2*i) = -1;
        Q(2*i+1) = -1;
    end
end
I(2*num_symbols+1) = I(2*num_symbols); % I holds last value while Q catches up

% create a single-period cosine for each phase shift and attach them end to end
for i = 1:2*num_symbols
    t = linspace(0,1,fs);
    OQPSK_signal(fs*(i-1)+1:fs*i) = cos(2*pi*t + angle(I(i)+1j*Q(i)));
end

% plot input symbols over the generated OQPSK wave
figure(1)
n1 = 0:fs*(2*num_symbols)-1;
n2 = 0:2*fs:2*fs*(num_symbols+1)-1;
stairs(n2, [symbols+1;symbols(num_symbols)+1])
hold on
plot(n1, OQPSK_signal)
xticks(0:2*fs:fs*(2*num_symbols)-1)
xticklabels({1:2*num_symbols-1})
yticks(-1:4)
yticklabels({'','','00','01','10','11'})
xlabel('Symbol')
legend('2-bit symbols','OQPSK signal','Location','southoutside')
grid on


