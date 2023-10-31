import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Checkbox extends JFrame {
    public static void main(String[] args) {
        // Create a JFrame (window) for the Checkbox frame
        JFrame framecheck = new JFrame("Checkbox Example");
        framecheck.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        framecheck.setSize(300, 150);

        // Create a JPanel to hold the checkboxes and button
        JPanel panel = new JPanel();

        // Create two checkboxes
        JCheckBox cpmCheckbox = new JCheckBox("CPM");
        JCheckBox pertCheckbox = new JCheckBox("PERT");

        // Create a submit button
        JButton submitButton = new JButton("Submit");

        // Add an action listener to the submit button
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Check which checkboxes are selected and perform actions accordingly
                if (cpmCheckbox.isSelected()) {
                    CPMGUI cpmGUI = new CPMGUI();
                    cpmGUI.setVisible(true);
                }
                else if (pertCheckbox.isSelected()) {
                    PERTCalculatorGUI2 pertGUI = new PERTCalculatorGUI2();
                    pertGUI.setVisible(true);
                }
            }
        });

        // Add the checkboxes and submit button to the panel
        panel.add(cpmCheckbox);
        panel.add(pertCheckbox);
        panel.add(submitButton);

        // Add the panel to the frame
        framecheck.add(panel);

        // Set the frame visible
        framecheck.setVisible(true);
    }
}
