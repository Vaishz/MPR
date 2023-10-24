import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;

class PERTTask {
    String name;
    int optimisticDuration;
    int mostLikelyDuration;
    int pessimisticDuration;
    double expected;
    double variance;
    double standardDeviation;

    PERTTask(String name, int optimisticDuration, int mostLikelyDuration, int pessimisticDuration) {
        this.name = name;
        this.optimisticDuration = optimisticDuration;
        this.mostLikelyDuration = mostLikelyDuration;
        this.pessimisticDuration = pessimisticDuration;

        calculatePERTValues();
    }

    private void calculatePERTValues() {
        expected = (optimisticDuration + 4 * mostLikelyDuration + pessimisticDuration) / 6.0;
        variance = ((pessimisticDuration - optimisticDuration) / 6.0) * ((pessimisticDuration - optimisticDuration) / 6.0);
        standardDeviation = Math.sqrt(variance);
    }
}

public class PERTCalculatorGUI {
    private List<PERTTask> tasks;
    private double projectTime;
    private double projectVariance;
    private double projectStandardDeviation;

    private JFrame frame;
    private JPanel inputPanel;
    private JPanel outputPanel;
    private JButton calculateButton;
    private JButton clearButton;
    private JTextArea outputTextArea;

    public PERTCalculatorGUI() {
        tasks = new ArrayList<>();
        frame = new JFrame("PERT Calculator");
        frame.setLayout(new BorderLayout());

        inputPanel = new JPanel();
        inputPanel.setLayout(new GridLayout(0, 3));

        JLabel nameLabel = new JLabel("Task Name");
        JLabel optimisticLabel = new JLabel("Optimistic Duration");
        JLabel mostLikelyLabel = new JLabel("Most Likely Duration");
        JLabel pessimisticLabel = new JLabel("Pessimistic Duration");
        JLabel dependenciesLabel = new JLabel("Dependencies (comma-separated)");

        JTextField nameField = new JTextField();
        JTextField optimisticField = new JTextField();
        JTextField mostLikelyField = new JTextField();
        JTextField pessimisticField = new JTextField();
        JTextField dependenciesField = new JTextField();

        calculateButton = new JButton("Calculate PERT");
        clearButton = new JButton("Clear Screen");
        outputTextArea = new JTextArea(10, 30);
        outputTextArea.setEditable(false);

        calculateButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String name = nameField.getText();
                int optimistic = Integer.parseInt(optimisticField.getText());
                int mostLikely = Integer.parseInt(mostLikelyField.getText());
                int pessimistic = Integer.parseInt(pessimisticField.getText());
                String[] dependencies = dependenciesField.getText().split(",");

                PERTTask task = new PERTTask(name, optimistic, mostLikely, pessimistic);
                tasks.add(task);

                for (String dep : dependencies) {
                    for (PERTTask t : tasks) {
                        if (t.name.equals(dep.trim())) {
                            // Assuming dependencies are names of tasks
                            // You can customize this part to link activities
                            // for critical path calculations
                        }
                    }
                }

                calculatePERT();
            }
        });

        clearButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                tasks.clear();
                projectTime = 0.0;
                projectVariance = 0.0;
                projectStandardDeviation = 0.0;
                outputTextArea.setText("");
            }
        });

        inputPanel.add(nameLabel);
        inputPanel.add(optimisticLabel);
        inputPanel.add(mostLikelyLabel);
        inputPanel.add(nameField);
        inputPanel.add(optimisticField);
        inputPanel.add(mostLikelyField);
        inputPanel.add(pessimisticLabel);
        inputPanel.add(dependenciesLabel);
        inputPanel.add(new JLabel(""));
        inputPanel.add(pessimisticField);
        inputPanel.add(dependenciesField);
        inputPanel.add(calculateButton);
        inputPanel.add(new JLabel(""));
        inputPanel.add(clearButton);

        outputPanel = new JPanel();
        outputPanel.add(outputTextArea);

        frame.add(inputPanel, BorderLayout.NORTH);
        frame.add(outputPanel, BorderLayout.SOUTH);

        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.pack();
        frame.setVisible(true);
    }

    private void calculatePERT() {
        double totalExpected = 0.0;
        double totalVariance = 0.0;

        for (PERTTask task : tasks) {
            double taskExpected = task.expected;
            double taskVariance = task.variance;

            // You can calculate dependencies here if needed

            task.expected = taskExpected;
            task.variance = taskVariance;

            totalExpected += taskExpected;
            totalVariance += taskVariance;
        }

        projectTime = totalExpected;
        projectVariance = totalVariance;
        projectStandardDeviation = Math.sqrt(totalVariance);

        displayPERTResults();
    }

    private void displayPERTResults() {
        DecimalFormat df = new DecimalFormat("#.##");

        outputTextArea.setText("PERT Project Time: " + df.format(projectTime) + "\n");
        outputTextArea.append("Variance of Total Project: " + df.format(projectVariance) + "\n");
        outputTextArea.append("Standard Deviation: " + df.format(projectStandardDeviation) + "\n");
        outputTextArea.append("Probability of Completion:\n");

        for (PERTTask task : tasks) {
            double probability = calculateProbability(task.expected, task.variance);
            outputTextArea.append(task.name + ": " + df.format(probability) + "\n");
        }
    }

    private double calculateProbability(double expected, double variance) {
        double z = (projectTime - expected) / projectStandardDeviation;
        return 1 - cumulativeDistribution(z);
    }

    private double cumulativeDistribution(double z) {
        double t = 1 / (1 + 0.2316419 * Math.abs(z));
        double y = (((((1.330274429 * t - 1.821255978) * t + 1.781477937) * t - 0.356563782) * t + 0.319381530) * t) / (2 * Math.PI) + 0.5;

        if (z > 0) {
            return 1 - y;
        } else {
            return y;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new PERTCalculatorGUI());
    }
}
