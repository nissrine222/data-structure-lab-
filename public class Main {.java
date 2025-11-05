public class Main {
    import java.awt.*;
import java.awt.event.*;

public class TestFramel extends Frame {

    TestFramel(String title) {
        super(title);
        setBounds(500, 300, 280, 150);
        setLayout(new FlowLayout());

        // Adding components
        Label lab1 = new Label("用户户名");
        add(lab1);
        TextField txt1 = new TextField(20);
        add(txt1);

        Label lab2 = new Label("PASS");
        add(lab2);
        TextField txt2 = new TextField(20);
        add(txt2);

        Button but1 = new Button("插入");
        add(but1);
        Button but2 = new Button("更新");
        add(but2);

        // Adding ActionListener to buttons
        but2.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                System.out.println("按钮点击了");
            }
        });

        setVisible(true);
    }

    public static void main(String[] args) {
        // Create an instance of the TestFramel class
        TestFramel newWindow = new TestFramel("系统登录");
    }
}
}
