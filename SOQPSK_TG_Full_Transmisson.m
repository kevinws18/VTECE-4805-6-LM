clc; clear; close all;

% Parameters specific to SOQPSK-TG
global T; global E; global SPS;
T = 1; E = 1; SPS = 20;

% Length of transmitted message
messageLength = 100;

% Preamble (MUST be at least of length 2 for ternary demodulation)
preamble = [0,0,1,1,0,1,1,0,0,0,0,0,0,0];
preambleLen = length(preamble);

% End value, ensures that entire message is modulated
endMsg = [0,0,0,0,0,0,0];
endMsgLen = length(endMsg);

% Generate message bits to be transmitted
message = randi([0 1],[1,messageLength]); % replace for custom message
% messageLength = length(message);  % uncomment for custom message

% Calculate total number of bits and randomly generate input bits
number_of_bits = preambleLen + messageLength + endMsgLen;
input_bits = [preamble, message, endMsg];

% Modulate and demodulate signal
signal = SOQPSK_TG_modulation(input_bits);
output_bits = SOQPSK_TG_demodulation(preamble, signal);

% Plot signal
fig = figure(1);
fig.Position = [100, 600, 1500, 400];
subplot(2,1,1);
hold on
plot(1:length(signal), real(signal));
plot(1:length(signal), imag(signal));
xlim([0 length(signal)]);
legend('real', 'imaginary','Location','NorthEastOutside');
title('SOQPSK TG signal');

% Plot bit comparison
subplot(2,1,2);
hold on
plot(1:number_of_bits, input_bits, 'o');
plot((1:number_of_bits), output_bits, '*');
xlim([0 number_of_bits]);
ylim([-0.5, 1.5]);
legend('Original', 'Demodulated','Location','NorthEastOutside');
title('Original vs Demodulated bits');

%% SOQPSK_TG modulation function
function signal = SOQPSK_TG_modulation(u)

    % Call parameters specific to SOQPSK-TG
    global T; global E; global SPS;
    number_of_bits = length(u);
    
    % (Standard) Ternary Precoder 
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
        tempsum = 0;
        for index2 = 1:length_procfTGs
            if index - index2 >= 1
                tempsum = tempsum + procfTGs(index2) * padded(index - index2 + 1);
            else
                break
            end 
        end
       result(index) =  tempsum;
    end
    
    % Cumulative Sum
    phase = zeros(1, length(result)); phase(1) = result(1);
    for index = 2:length(result)
        phase(index) = phase(index-1) + result(index);
    end

    % SOQPSK-TG signal baseband representation
    signal = sqrt(E/T).*exp(1i*pi*(phase + 0.25));
end

%% SOQPSK_TG demodulation function
function bits = SOQPSK_TG_demodulation(preamble, signal)
    
    global SPS;    
    samples_per_bit = SPS/2;

    % Reconstruct phase by unwrapping the angle of the signal
    phase = (unwrap(angle(signal)) - 0.785416) / pi;
    
    filtered = zeros(1,length(phase));
    for i = 2:length(phase)-1
        filtered(i) = phase(i+1) - phase(i);
    end
    
    % Reconstruct pre filter design by normalizing post-filter signal to
    %   [0,1]
    % Offset value to act as threshold for the zero ternary val
    filter_offset = 0.015;
    padded = zeros(1,length(phase));
    for i = 1:length(padded)
        if(filtered(i) > filter_offset)
            padded(i) = 1;
        elseif (filtered(i) < -filter_offset)
            padded(i) = -1;
        end
    end
    
    % Reconstruct ternary by sampling [padded] by num samples per bit
    alpha = zeros(1,length(padded)/samples_per_bit);
    for i = 2:length(alpha)
        alpha(i) = padded((i-1)*samples_per_bit);
    end
    
    % Reconstruct bits by starting with last two preamble bits and
    % calculating third bit using ternary result
    starter = preamble(end-2+1:end);
    bits = zeros(1,length(alpha));
    bits(1) = starter(1); bits(2) = starter(2); 
    for k = 3:length(alpha)
        if ((-1)^(k+1))*(2*bits(k-1) - 1)*(1 - bits(k-2)) == alpha(k)
            bits(k) = 1;
        end
    end
    
    % cut out 4 bits that were generated due to the application of the precoder twice 
    bits = [bits(5:end) [0,0,0,0]];
end
