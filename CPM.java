import javax.swing.*;
import java.awt.*;
import java.util.*;
import java.util.List;

class Activity {
    String name;
    int duration;
    List<Activity> dependencies;
    int earliestStart;
    int earliestFinish;
    int latestStart;
    int latestFinish;
    int slack;

    Activity(String name, int duration) {
        this.name = name;
        this.duration = duration;
        this.dependencies = new ArrayList<>();
    }

    void addDependency(Activity activity) {
        dependencies.add(activity);
    }
}

class CPMDiagramPanel extends JPanel {
    private List<Activity> criticalPath;

    public CPMDiagramPanel(List<Activity> criticalPath) {
        this.criticalPath = criticalPath;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Add code here to draw the CPM diagram based on the critical path.
        // You can customize the drawing as per your requirements.
        g.drawString("CPM Diagram", 10, 20);

        int x = 10;
        for (Activity activity : criticalPath) {
            g.drawString(activity.name, x, 50);
            x += 80;
        }
    }
}

public class CPM {
    private List<Activity> activities;
    private List<Activity> criticalPath;
    private int cpmTime;

    public CPM() {
        activities = new ArrayList<>();
        criticalPath = new ArrayList<>();
        cpmTime = 0;
    }

    public void addActivity(Activity activity) {
        activities.add(activity);
    }

    public void calculateCPM() {
        // Calculate earliest start and finish times for the first activity
        Activity startActivity = activities.get(0);
        startActivity.earliestStart = 0;
        startActivity.earliestFinish = startActivity.duration;

        // Perform forward pass
        for (int i = 1; i < activities.size(); i++) {
            Activity currentActivity = activities.get(i);

            // Calculate earliest start and finish times for 'currentActivity'
            int maxEarliestFinish = 0;
            for (Activity dependency : currentActivity.dependencies) {
                if (dependency.earliestFinish > maxEarliestFinish) {
                    maxEarliestFinish = dependency.earliestFinish;
                }
            }
            currentActivity.earliestStart = maxEarliestFinish;
            currentActivity.earliestFinish = currentActivity.earliestStart + currentActivity.duration;
        }

        // Calculate latest start and finish times for the last activity
        Activity endActivity = activities.get(activities.size() - 1);
        endActivity.latestFinish = endActivity.earliestFinish;
        endActivity.latestStart = endActivity.latestFinish - endActivity.duration;

        criticalPath.add(endActivity);

        // Perform backward pass
        for (int i = activities.size() - 2; i >= 0; i--) {
            Activity currentActivity = activities.get(i);

            // Calculate latest start and finish times for 'currentActivity'
            int minLatestStart = Integer.MAX_VALUE;
            for (Activity dependentActivity : activities) {
                if (dependentActivity.dependencies.contains(currentActivity)) {
                    int latestStart = dependentActivity.latestStart - currentActivity.duration;
                    if (latestStart < minLatestStart) {
                        minLatestStart = latestStart;
                    }
                }
            }
            currentActivity.latestStart = minLatestStart;
            currentActivity.latestFinish = currentActivity.latestStart + currentActivity.duration;

            // Calculate slack for 'currentActivity'
            currentActivity.slack = currentActivity.latestStart - currentActivity.earliestStart;

            // Check if 'currentActivity' is on the critical path
            if (currentActivity.slack == 0 || (currentActivity == endActivity)) {
                criticalPath.add(currentActivity);
            }
        }

        // Calculate the CPM time (earliest finish time of the last activity on the critical path)
        cpmTime = endActivity.earliestFinish;
    }

    public List<Activity> getCriticalPath() {
        return criticalPath;
    }

    public int getCPMTime() {
        return cpmTime;
    }

    public static void main(String[] args) {
        CPM cpm = new CPM();
        Scanner scanner = new Scanner(System.in);

        // Allow the user to input activities and their details
        while (true) {
            System.out.print("Enter activity name (or 'done' to finish): ");
            String name = scanner.nextLine();

            if (name.equals("done")) {
                break;
            }

            System.out.print("Enter duration: ");
            int duration = Integer.parseInt(scanner.nextLine());

            Activity activity = new Activity(name, duration);

            System.out.print("Enter dependencies (comma-separated, or press Enter if none): ");
            String dependencyLine = scanner.nextLine();
            String[] dependencies = dependencyLine.split(",");

            for (String dependency : dependencies) {
                String trimmedDependency = dependency.trim();
                if (!trimmedDependency.isEmpty()) {
                    // Add the specified dependencies
                    Activity dependencyActivity = cpm.activities.stream()
                            .filter(a -> a.name.equals(trimmedDependency))
                            .findFirst()
                            .orElse(null);
                    if (dependencyActivity != null) {
                        activity.addDependency(dependencyActivity);
                    }
                }
            }

            cpm.addActivity(activity);
        }

        // Calculate the Critical Path and CPM time
        cpm.calculateCPM();

        // Display the Critical Path and CPM time
        System.out.println("\nCritical Path:");
        List<Activity> criticalPath = cpm.getCriticalPath();

        for (int i = criticalPath.size() - 1; i >= 0; i--) {
            Activity activity = criticalPath.get(i);
            System.out.println(activity.name);
        }

        System.out.println("\nCPM Time: " + cpm.getCPMTime());

        // Create and show the GUI
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("CPM Diagram");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.getContentPane().add(new CPMDiagramPanel(criticalPath));
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}
