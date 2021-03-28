clc; clear; close all;

% Parameters specific to SOQPSK-TG
global T; global E; global SPS;
T = 1; E = 1; SPS = 20;

% Random bitstream generation
number_of_bits = 500;
u = randi([0 1],[1,number_of_bits]);

% (Standard) Ternary Precorder 
alpha = zeros(1,number_of_bits);
for k = 3:number_of_bits
    alpha(k) = ((-1)^(k+1))*(2*u(k-1) - 1)*(u(k) - u(k-2));
end

% Normalized Partial-Resposne Frequency Pulse
global procfTGs;
procfTGs = getfield(load('procfTGs.mat'), 'procfTGs');

% Zero Padding
padded = zeros(1, length(alpha)*(SPS/2));
for index = 1:length(alpha)
    padded((index-1)*SPS/2 + 1) = alpha(index);
end

% Filter Function
length_padded = length(padded); 
length_procfTGs = length(procfTGs);
result = zeros(1, length_padded);
for index = 1:length_padded
    sum = 0;
    for index2 = 1:length_procfTGs
        if index - index2 >= 1
            sum = sum +  procfTGs(index2) * padded(index - index2 + 1);
        end
    end
   result(index) =  sum;
end
%filt = filter(procfTGs, 1, padded);
%plot(1:5000, result);
%hold on
%plot(1:5000, filt);
%hold off
%legend('result', 'filt')

% Cumulative Sum
phase = zeros(1, length(result)); phase(1) = result(1);
for index = 2:length(result)
    phase(index) = phase(index-1) + result(index);
end

% SOQPSK-TG signal baseband representation
signal = sqrt(E/T).*exp(1i*pi*(phase + 0.25));

% Eye Diagram 
eyediagram(signal, 2*SPS, 2*pi, 0, 'r-')

figure('Name','SOQPSK signal', 'Position', [100 100 1000 500]);
plot(1:length(signal), signal)
