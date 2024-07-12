package textAreaComponent;

import services.MainService;
import textAreaComponent.textAreaEvents.TextChangeEvent;

import javax.swing.*;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;

public class TextAreaFocus implements FocusListener {
    @Override
    public void focusGained(FocusEvent e) {
        String text = ((JTextArea) e.getSource()).getText();
        onTextChange(e, text);
//        System.out.println(text);
    }

    @Override
    public void focusLost(FocusEvent e) {
        String text = ((JTextArea) e.getSource()).getText();
        onTextChange(e, text);
//        System.out.println(text);
    }

    public void onTextChange(FocusEvent e, String text) {
        TextChangeEvent event = new TextChangeEvent(e.getComponent(), text);

        MainService.INSTANCE.eventBus.post(event);
    }
}
