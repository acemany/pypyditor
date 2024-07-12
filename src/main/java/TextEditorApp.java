import groovy.lang.Singleton;
import services.MainService;
import textAreaComponent.TextAreaComponent;

import javax.swing.*;

@Singleton
public class TextEditorApp extends JFrame {
    public static void main(String[] args) {
        TextEditorApp frame = new TextEditorApp();

        frame.setVisible(true);
    }

    private TextEditorApp() {
        init();


        setBounds(100,100,687,586);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

    }

    public void init() {
        MainService.INSTANCE.eventBus.register(new TextChangeHandler());

        TextAreaComponent textArea = new TextAreaComponent();
        add(textArea);
    }

}
