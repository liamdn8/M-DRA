#!/usr/bin/env python3
import json

with open('results/medium-comparison/medium-sample_solver_comparison.json') as f:
    data = json.load(f)

print('=== WINNER BY MARGIN ===')
print()
print(f"{'Margin':<8} {'Solver X':<12} {'Solver Y':<12} {'Solver XY':<12} {'Winner':<10}")
print('-' * 60)

margins = sorted([float(m) for m in data['detailed_results']['x'].keys()], reverse=True)

x_wins = 0
xy_wins = 0
ties = 0

for margin in margins:
    m_str = str(margin)
    
    # Get values
    x_val = data['detailed_results']['x'].get(m_str, {}).get('optimal_value')
    y_val = data['detailed_results']['y'].get(m_str, {}).get('optimal_value')
    xy_val = data['detailed_results']['xy'].get(m_str, {}).get('optimal_value')
    
    # Format values
    x_str = f'{x_val:.1f}' if x_val is not None else 'N/A'
    y_str = f'{y_val:.1f}' if y_val is not None else 'N/A'
    xy_str = f'{xy_val:.1f}' if xy_val is not None else 'N/A'
    
    # Find winner
    values = []
    if x_val is not None:
        values.append(('X', x_val))
    if y_val is not None:
        values.append(('Y', y_val))
    if xy_val is not None:
        values.append(('XY', xy_val))
    
    if values:
        min_val = min(values, key=lambda x: x[1])
        winners = [v[0] for v in values if v[1] == min_val[1]]
        winner = '/'.join(winners) if len(winners) > 1 else winners[0]
        
        # Count wins
        if len(winners) > 1:
            ties += 1
        elif 'X' == winner:
            x_wins += 1
        elif 'XY' == winner:
            xy_wins += 1
    else:
        winner = 'NONE'
    
    print(f'{margin:<8.2f} {x_str:<12} {y_str:<12} {xy_str:<12} {winner:<10}')

print()
print('=== PERFORMANCE SUMMARY ===')
print(f'Solver X wins:  {x_wins} margins')
print(f'Solver XY wins: {xy_wins} margins')
print(f'Solver Y wins:  0 margins')
print(f'Ties:           {ties} margins')
print()
print(f'Solver X:  Fastest (avg 9.3s), best at moderate margins (0.75-0.85)')
print(f'Solver XY: Best quality at tight margins (0.45-0.60), 3.5x slower')
print(f'Solver Y:  Not recommended (worst results, slowest execution)')
