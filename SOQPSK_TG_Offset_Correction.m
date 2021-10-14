clc; clear; close all;

% Parameters specific to SOQPSK-TG
global T; global E; global SPS;
T = 1; E = 1; SPS = 20;

global CFO; global phaseOffset;
CFO = 0.020; phaseOffset = 0.005;   % Change values to simulate CFO and Phase offset

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

% Modulate and offset signal
signal = SOQPSK_TG_modulation(input_bits);
nn = 1:length(signal);
offset_signal = signal .* exp(1i*2*pi*(CFO.*nn - phaseOffset));


% Send correction packet
correction_bits = 100;
correction_packet = SOQPSK_TG_modulation(zeros(1,correction_bits));
correctnn = 1:length(correction_packet);
correction_packet = correction_packet .* exp(1i*2*pi*(CFO.*correctnn - phaseOffset));
% Calculate CFO
signal_unwrap = unwrap(angle(correction_packet));
calcCenterFrequencyOffset = ((signal_unwrap(end) - signal_unwrap(1))/(correction_bits))/62.7690;


% Send correction packet 2
correction_packet_2 = SOQPSK_TG_modulation(zeros(1,correction_bits));
correction_packet_2 = correction_packet_2 .* exp(1i*2*pi*(CFO.*correctnn - phaseOffset));
% Correct CFO in correction packet 2
correction_packet_2 = correction_packet_2 .* exp(1i*2*pi*(-calcCenterFrequencyOffset.*correctnn));
% Calculate Phase offset
signal_unwrap_2 = unwrap(angle(correction_packet_2));
calcPhaseOffset = ((signal_unwrap_2(1) - 0.791681)/-6.2832) - 0.00099;

% Corrected Signal
corrected_signal = offset_signal .* exp(1i*2*pi*(-calcCenterFrequencyOffset.*nn + calcPhaseOffset));

% Plot origial and offset angles
fig = figure(2);
fig.Position = [100, 100, 1500, 800];
subplot(2,1,1);
hold on
plot(1:length(signal), real(signal));
plot(1:length(signal), imag(signal));
plot(1:length(signal), angle(signal));
plot(1:length(signal), unwrap(angle(signal)));
legend('signal', 'angle', 'unwrapped angle');
title('raw signal');
subplot(2,1,2);
%plot(1:length(signalc), unwrap(real(signalc)));
hold on
plot(1:length(offset_signal), real(offset_signal));
plot(1:length(offset_signal), imag(offset_signal));
plot(1:length(offset_signal), angle(offset_signal));
plot(1:length(offset_signal), unwrap(angle(offset_signal)));
legend('signal', 'angle', 'unwrapped angle');
title('offset - frequency: ' + string(CFO) + ', phase: ' + string(phaseOffset));

% Plot orginial signal
fig = figure(1);
fig.Position = [100, 100, 1500, 800];
subplot(3,1,1);
hold on
plot(1:length(signal), real(signal));
plot(1:length(signal), imag(signal));
xlim([0 length(signal)]);
legend('real', 'imaginary','Location','NorthEastOutside');
title('SOQPSK TG Original Signal');

% Plot offset signal
subplot(3,1,2);
hold on
plot(1:length(offset_signal), real(offset_signal));
plot(1:length(offset_signal), imag(offset_signal));
xlim([0 length(offset_signal)]);
legend('real', 'imaginary','Location','NorthEastOutside');
title('SOQPSK TG Offset Signal - frequency: ' + string(CFO) + ', phase: ' + string(phaseOffset)');

% Plot corrected signal
subplot(3,1,3);
hold on
plot(1:length(corrected_signal), real(corrected_signal));
plot(1:length(corrected_signal), imag(corrected_signal));
xlim([0 length(corrected_signal)]);
legend('real', 'imaginary','Location','NorthEastOutside');
title('SOQPSK TG Corrected Signal - calculated frequency: ' + string(calcCenterFrequencyOffset) + ', phase: ' + string(calcPhaseOffset)');


% SOQPSK_TG modulation function
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
