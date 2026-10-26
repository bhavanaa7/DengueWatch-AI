import { render, screen } from '@testing-library/react';
import RiskBadge from './RiskBadge';

describe('RiskBadge', () => {
  it('renders the risk label', () => {
    render(<RiskBadge risk="High" />);
    expect(screen.getByText('High risk')).toBeInTheDocument();
  });
});
