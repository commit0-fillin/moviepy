import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

def sliders(f, sliders_properties, wait_for_validation=False):
    """ A light GUI to manually explore and tune the outputs of 
        a function.
        slider_properties is a list of dicts (arguments for Slider )
        
        def volume(x,y,z):
            return x*y*z
    
        intervals = [ { 'label' :  'width',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'height',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'depth',  'valmin': 1 , 'valmax': 5 } ]
        inputExplorer(volume,intervals)
    """
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25, bottom=0.25)
    
    # Hide the axes
    ax.set_frame_on(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Create sliders
    sliders = []
    for i, properties in enumerate(sliders_properties):
        ax_slider = plt.axes([0.25, 0.1 + 0.05 * i, 0.65, 0.03])
        slider = Slider(ax=ax_slider, **properties)
        sliders.append(slider)
    
    # Create a text box to show the output
    output_text = ax.text(0.5, 0.5, '', ha='center', va='center')
    
    # Update function
    def update(val):
        inputs = [slider.val for slider in sliders]
        result = f(*inputs)
        output_text.set_text(f"Output: {result}")
        fig.canvas.draw_idle()
    
    # Connect update function to sliders
    for slider in sliders:
        slider.on_changed(update)
    
    # Create a "Done" button if wait_for_validation is True
    if wait_for_validation:
        done_button_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
        done_button = Button(done_button_ax, 'Done')
        
        def on_done(event):
            plt.close(fig)
        
        done_button.on_clicked(on_done)
    
    # Initial call to update function
    update(None)
    
    # Show the plot
    plt.show()
    
    # Return the final values
    return [slider.val for slider in sliders]
