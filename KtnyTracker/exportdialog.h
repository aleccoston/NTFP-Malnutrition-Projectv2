#ifndef EXPORTDIALOG_H
#define EXPORTDIALOG_H

#include <QDialog>

namespace Ui {
class exportDialog;
}

class exportDialog : public QDialog
{
    Q_OBJECT

public:
    explicit exportDialog(QWidget *parent = 0);
    ~exportDialog();

private:
    Ui::exportDialog *ui;
};

#endif // EXPORTDIALOG_H
