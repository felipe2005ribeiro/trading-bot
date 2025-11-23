"""
Trailing stop update method to add to Position class.
Insert this after the should_close method.
"""

def update_trailing_stop(self, current_price: float, config) -> bool:
    """
    Update trailing stop based on current price and configuration.
    
    Args:
        current_price: Current market price
        config: Configuration object with trailing stop parameters
    
    Returns:
        True if trailing stop was updated, False otherwise
    """
    if not config.ENABLE_TRAILING_STOP:
        return False
    
    # Calculate current unrealized profit percentage
    pnl, pnl_percent = self.calculate_pnl(current_price)
    
    # Check if we should activate trailing stop
    if not self.trailing_stop_active:
        if pnl_percent >= config.TRAILING_ACTIVATION_PERCENT:
            self.trailing_stop_active = True
            self.highest_price = current_price if self.side.lower() == 'buy' else self.entry_price
            self.lowest_price = self.entry_price if self.side.lower() == 'buy' else current_price
            
            # Calculate initial trailing stop price
            if self.side.lower() == 'buy':
                self.trailing_stop_price = current_price * (1 - config.TRAILING_DISTANCE_PERCENT / 100)
            else:
                self.trailing_stop_price = current_price * (1 + config.TRAILING_DISTANCE_PERCENT / 100)
            
            return True  # Trailing stop just activated
    
    # If already active, update highest/lowest and trailing stop
    if self.trailing_stop_active:
        updated = False
        
        if self.side.lower() == 'buy':
            # For buy positions, track highest price
            if current_price > self.highest_price:
                self.highest_price = current_price
                new_trailing_stop = current_price * (1 - config.TRAILING_DISTANCE_PERCENT / 100)
                
                # Only move trailing stop up, never down
                if new_trailing_stop > self.trailing_stop_price:
                    self.trailing_stop_price = new_trailing_stop
                    updated = True
        else:
            # For sell positions, track lowest price
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                new_trailing_stop = current_price * (1 + config.TRAILING_DISTANCE_PERCENT / 100)
                
                # Only move trailing stop down, never up
                if new_trailing_stop < self.trailing_stop_price:
                    self.trailing_stop_price = new_trailing_stop
                    updated = True
        
        return updated
    
    return False
