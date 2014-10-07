#include "exportdialog.h"
#include "ui_exportdialog.h"

exportDialog::exportDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::exportDialog)
{
    ui->setupUi(this);
}

exportDialog::~exportDialog()
{
    delete ui;
}
