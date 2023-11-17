import ntplib
from typing import List, Tuple


# Função para obter o tempo de um servidor NTP e o RTT associado
def get_ntp_time(server: str) -> Tuple[float, float]:
    client = ntplib.NTPClient()
    response = client.request(server, version=3)
    ntp_time = response.tx_time
    rtt = response.root_delay / 2  # Aproximação do RTT
    return ntp_time, rtt


# Algoritmo de Marzullo modificado para sincronização de tempo
def marzullo_ntp(timestamps: List[Tuple[float, float]]) -> Tuple[float, float]:
    intervals = []
    for ntp_time, error_margin in timestamps:
        intervals.append((ntp_time - error_margin, 1))  # Ponto de início
        intervals.append((ntp_time + error_margin, -1))  # Ponto de fim

    sorted_intervals = sorted(intervals, key=lambda x: (x[0], -x[1]))
    best_interval = (None, None)
    max_count = 0
    current_count = 0

    for point, type in sorted_intervals:
        current_count += type
        if current_count > max_count:
            max_count = current_count
            best_interval = (point, point)
        elif current_count == max_count:
            best_interval = (best_interval[0], point)

    # Calcula o ponto médio do melhor intervalo como o tempo de consenso
    consensus_time = (best_interval[0] + best_interval[1]) / 2
    return consensus_time, max_count


# Lista de servidores NTP
ntp_servers = ['pool.ntp.org', 'time.nist.gov', 'time.google.com']

# Obter o tempo e o RTT de cada servidor
timestamps = []
for server in ntp_servers:
    try:
        ntp_time, rtt = get_ntp_time(server)
        timestamps.append((ntp_time, rtt))
    except ntplib.NTPException:
        print(f"Failed to get time from {server}")

# Aplicar o algoritmo de Marzullo
if timestamps:
    consensus_time, _ = marzullo_ntp(timestamps)
    print(f"Consensus time is {consensus_time}")
else:
    print("No NTP responses were received.")
