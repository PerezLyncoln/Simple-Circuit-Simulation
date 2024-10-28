from flask import Flask, render_template, request, send_file
import matplotlib.pyplot as plt
import matplotlib.patches as patches 
import io

app = Flask(__name__)

# Calculates the total resistance based on the circuit type
def calculate_total_resistance(resistances, circuit_type):
    if circuit_type == 'series': # Series circuit finds the total resistance by adding every value (r = r1 + r2 + r3 + ... rn)
        return sum(resistances)
    elif circuit_type == 'parallel': # Parallel circuit finds the total resistance by adding every value over 1 (r = 1/r1 + 1/r2 + 1/r3 + ... + 1/rn)
        return 1 / sum(1 / r for r in resistances if r != 0)  # [r !=0] Handles zero inputs to avoid division by zero

# Function to call to graph the circuit
def draw_circuit(resistances, circuit_type):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    total_components = len(resistances) + 1  # Includes 1 capacitor
    components = resistances + ['C']  # One capacitor at the end

    # If choosen circuit type is Series
    if circuit_type == 'series':
        # Draw the outer loop to complete the whole circuit
        ax.plot([0, total_components + 1], [0, 0], 'k')  # Top horizontal line
        ax.plot([0, 0], [0, -1], 'k')  # Left vertical line
        ax.plot([total_components + 1, total_components + 1], [0, -1], 'k')  # Right vertical line
        
        for i, component in enumerate(components):
            # Draw horizontal wire for each component
            ax.plot([i, i + 1], [0, 0], 'k')  # Wire for each component
            if component == 'C':  # Capacitor
                ax.plot([i + 0.45, i + 0.45], [-0.1, 0.1], 'k', lw=3)
                ax.plot([i + 0.55, i + 0.55], [-0.1, 0.1], 'k', lw=3)
                ax.text(i + 0.5, -0.4, 'C', ha='center')
            else:
                # Draw resistor as a rectangle
                rect = patches.Rectangle((i + 0.25, -0.1), 0.5, 0.2, edgecolor='black', facecolor='lightgray')
                ax.add_patch(rect)
                ax.text(i + 0.5, -0.4, f'R{i + 1} = {component}Ω', ha='center')
        # Draw the bottom horizontal line connecting both vertical lines
        ax.plot([0, total_components + 1], [-1, -1], 'k')  # Bottom horizontal line
    
    # If choosen circuit type is Parallel
    elif circuit_type == 'parallel':
        for i, component in enumerate(components):
            ax.plot([0, 1], [-i, -i], 'k')  # Horizontal wire for each component
            if component == 'C':  # Capacitor
                ax.plot([0.45, 0.45], [-i + 0.1, -i - 0.1], 'k', lw=3)
                ax.plot([0.55, 0.55], [-i + 0.1, -i - 0.1], 'k', lw=3)
                ax.text(0.5, -i - 0.4, 'C', ha='center')
            else:
                rect = patches.Rectangle((0.25, -i - 0.1), 0.5, 0.2, edgecolor='black', facecolor='lightgray') # Use to graph the resistors presented as rectangles
                ax.add_patch(rect)
                ax.text(0.5, -i - 0.4, f'R{i + 1} = {component}Ω', ha='center')
        ax.plot([0, 0], [0, -total_components + 1], 'k')  # Left vertical wire
        ax.plot([1, 1], [0, -total_components + 1], 'k')  # Right vertical wire
    
    ax.axis('off')

    # Calculate and display total resistance for the selected circuit type
    total_resistance = calculate_total_resistance(resistances, circuit_type)
    plt.title(f'{circuit_type.capitalize()} Circuit\nTotal Resistance: {total_resistance:.2f} Ω')

    # Used to store the graphical presentation of a circuit and turn it into a image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    try:
        resistances = list(map(float, request.form['resistances'].split(','))) # Converts user input into integer/float value
        if not resistances:
            raise ValueError("No resistance values provided.")

        # Takes the circuit type input from the form
        circuit_type = request.form['circuit_type']

        # Display the circuit image
        buf = draw_circuit(resistances, circuit_type)
        return send_file(buf, mimetype='image/png')
    
    # To catch any wrong input values in the form
    except ValueError as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
