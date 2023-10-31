package javaapplication2;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class Checkbox1 extends Frame {
    public static void main(String[] args) {
        // Create a Frame (window) for the Checkbox frame
        Checkbox1 framecheck1 = new Checkbox1();
        framecheck1.setTitle("Checkbox Example");
        framecheck1.setSize(300, 150);
        framecheck1.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent we) {
                System.exit(0);
            }
        });

        // Create a Panel to hold the checkboxes and button
        Panel panel = new Panel();

        // Create two checkboxes from java.awt.Checkbox
        Checkbox cpmCheckbox = new Checkbox("CPM");
        Checkbox pertCheckbox = new Checkbox("PERT");

        // Create a submit button
        Button submitButton = new Button("Submit");

        // Add an action listener to the submit button
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Check which checkboxes are selected and perform actions accordingly
                if (cpmCheckbox.getState()) {
                    CPMGUI1 cpmGUI1 = new CPMGUI1();
                    cpmGUI1.setVisible(true);
                } else if (pertCheckbox.getState()) {
                    PERTCalculatorGUI1 pertGUI1 = new PERTCalculatorGUI1();
                    pertGUI1.setVisible(true);
                }
            }
        });

        // Add the checkboxes and submit button to the panel
        panel.add(cpmCheckbox);
        panel.add(pertCheckbox);
        panel.add(submitButton);

        // Add the panel to the frame
        framecheck1.add(panel);

        // Set the frame visible
        framecheck1.setVisible(true);
    }
}
