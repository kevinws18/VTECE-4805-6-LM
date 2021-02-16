clear
clc

% Uses OQPSK modulation scheme to map 2-bit symbols to phase-shifts (PSK = phase-shift keying)
%TODO: turn this into SOQPSK-TG modulation (They should be similar?)
%TODO: maybe use awgn to add noise to simulate RF transmission


% specify your own symbols
%symbols = [0; 0; 0; 0; 0; 0; 0; 0; 0; 0];
%size = size(symbols);
%num_symbols = size(:,1);

% or create random symbols
num_symbols = 10;
symbols = randi([0 3],num_symbols,1);

% create modulation scheme
% currently no pulse-shaping (is this what makes it SOQPSK?)
% takes 2-bit integers [0 to 3] as input
sps = 2; % samples per symbol (this is why there are two phases per symbol, i think this prevents jumps > 90deg)
oqpskmod = comm.OQPSKModulator(pi/4,'PulseShape','Custom','FilterNumerator',[1],'SamplesPerSymbol',sps,'BitInput',false);

% modulate input
signal = oqpskmod(symbols);

% I think this one is more realistic???
% ^ A baseband signal is frequencies near 0
% rn i'm not using it
filtered_signal = lowpass(signal,1,1000);


% plot symbols alongside corresponding phases
figure(1)
grid on
title('Mapping Symbols to Phases')
xlabel('Symbol')
hold on
stairs(0:num_symbols,[symbols;symbols(num_symbols)],'b')
for i = 1:num_symbols*sps
    n = (i-1)/sps:1e-2:i/sps;
    y = cos(n*2*pi*sps+phase(signal(i)))-1;
    plot(n,y,'r')
end
xticks(0:num_symbols)
yticks(0:3)
yticklabels({'00','01','10','11'})
legend('2-bit symbol','phase','Location','southoutside')
hold off

m = 0:1/sps:num_symbols;
figure(2)
stairs(0:num_symbols,[symbols+3; symbols(num_symbols)+3], 'b')
hold on
stairs(m,[angle(signal); angle(signal(num_symbols*sps))], 'r')
title('Mapping Symbols to Phases')
xticks(0:10)
yticks([-3*pi/4:pi/2:3*pi/4, 3, 4, 5, 6])
yticklabels({'-3\pi/4','-\pi/4','\pi/4','3\pi/4','00','01','10','11'})
legend('2-bit symbol','phase','Location','southoutside')
grid on
