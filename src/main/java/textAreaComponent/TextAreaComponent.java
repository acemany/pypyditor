package textAreaComponent;

import com.google.common.eventbus.EventBus;

import javax.swing.*;

public class TextAreaComponent extends JTextArea {
    private final EventBus eventBus = new EventBus();
    private final TextAreaFocus TextAreaFocus = new TextAreaFocus();

    public TextAreaComponent() {
//        eventBus.post('init', () -> 'afaf');
        addFocusListener(TextAreaFocus);
    }
}
